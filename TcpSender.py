import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from visualization_msgs.msg import Marker
from geometry_msgs.msg import Point
import socket
import threading
import sqlite3

class TcpSenderReceiverNode(Node):
    def __init__(self):
        super().__init__('tcp_sender_receiver_node')

        # Configuration du client TCP pour envoyer des données au FiPy
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.fipy_ip = '10.89.2.196'  # Adresse IP du FiPy
        self.fipy_port = 1234

        try:
            self.get_logger().info('Connexion au FiPy...')
            self.client_socket.connect((self.fipy_ip, self.fipy_port))
            self.get_logger().info('Connecté au FiPy')
        except socket.error as e:
            self.get_logger().error(f'Erreur de connexion au FiPy: {e}')
            self.client_socket = None

        # Configuration du serveur TCP pour recevoir des données
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_ip = '0.0.0.0'  # Écouter sur toutes les interfaces
        self.server_port = 1235

        self.server_socket.bind((self.server_ip, self.server_port))
        self.server_socket.listen(1)
        self.get_logger().info(f'Serveur TCP en écoute sur {self.server_ip}:{self.server_port}')

        # Lancer un thread pour accepter les connexions entrantes
        self.tcp_thread = threading.Thread(target=self.accept_connections)
        self.tcp_thread.start()

        # Souscriptions
        self.pose_subscription = self.create_subscription(Odometry, '/odom', self.pose_callback, 10)

        # Publisher pour les marqueurs RViz
        self.marker_publisher = self.create_publisher(Marker, '/temperature_marker', 10)

        # Stockage des dernières valeurs reçues
        self.current_position = None
        self.current_temperature = None

        # ID unique pour chaque marqueur
        self.marker_id = 0

        # Timer pour envoyer les données de position
        self.create_timer(5.0, self.send_position_data)

        # Connexion à la base de données SQLite
        self.db_connection = sqlite3.connect('temperature_data.db')
        self.db_cursor = self.db_connection.cursor()
        self.create_table()

    def create_table(self):
        # Création de la table pour stocker les données de température et de position
        self.db_cursor.execute('''
            CREATE TABLE IF NOT EXISTS temperature_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                temperature REAL,
                position_x REAL,
                position_y REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.db_connection.commit()

    def insert_data(self, temperature, position_x, position_y):
        # Insertion des données de température et de position dans la base de données
        self.db_cursor.execute('''
            INSERT INTO temperature_data (temperature, position_x, position_y)
            VALUES (?, ?, ?)
        ''', (temperature, position_x, position_y))
        self.db_connection.commit()

    def accept_connections(self):
        while True:
            conn, _ = self.server_socket.accept()
            self.get_logger().info('Connexion acceptée')
            try:
                while True:
                    data = conn.recv(1024).decode()
                    if not data:
                        break

                    # Traitement des données reçues
                    self.get_logger().info(f'Données reçues: {data.strip()}')

                    if data.startswith('Temperature:'):
                        temperature = data.split(':')[1].strip()

                        # Suppression de l'unité de température avant conversion
                        temperature_value = temperature.replace('C', '').strip()

                        try:
                            self.current_temperature = float(temperature_value)
                            if self.current_position is not None:
                                self.insert_data(self.current_temperature, self.current_position.x, self.current_position.y)
                            self.publish_marker()
                        except ValueError:
                            self.get_logger().error(f"Erreur lors de la conversion de la température: '{temperature}'")

                    elif data.startswith('Position:'):
                        position_data = data.split(':')[1].strip()
                        x, y = map(float, position_data.split(','))
                        self.current_position = self.create_position(x, y)
                        self.publish_marker()

                    else:
                        self.get_logger().info(f'Message reçu: {data}')

                    # Envoyer une réponse au client après traitement
                    conn.send('Message reçu et traité\n'.encode())

            except OSError as e:
                self.get_logger().error(f'Erreur de connexion: {e}')
            finally:
                conn.close()
                self.get_logger().info('Connexion fermée')

    def create_position(self, x, y):
        position = Point()
        position.x = x
        position.y = y
        position.z = 0
        return position

    def pose_callback(self, msg):
        # Utiliser les coordonnées reçues pour mettre à jour la position
        self.current_position = msg.pose.pose.position
        #self.current_temperature += 0.01
        self.publish_marker()

    def publish_marker(self):
        if self.current_position is not None and self.current_temperature is not None:
            marker = Marker()
            marker.header.frame_id = "map"
            marker.header.stamp = self.get_clock().now().to_msg()
            marker.type = Marker.SPHERE
            marker.action = Marker.ADD

            # Position du marqueur
            marker.pose.position = self.current_position
            marker.pose.orientation.w = 1.0

            # Taille du marqueur
            marker.scale.x = 0.5
            marker.scale.y = 0.5
            marker.scale.z = 0.5

            # Couleur en fonction de la température
            if self.current_temperature > 30.0:
                marker.color.r = 1.0
                marker.color.g = 0.0
                marker.color.b = 0.0
            elif 20.0 < self.current_temperature <= 30.0:
                marker.color.r = 1.0
                marker.color.g = 1.0
                marker.color.b = 0.0
            else:
                marker.color.r = 0.0
                marker.color.g = 0.0
                marker.color.b = 1.0

            marker.color.a = 1.0

            # Utiliser un ID unique pour chaque marqueur
            marker.id = self.marker_id
            self.marker_id += 1

            # Publier le marqueur
            self.marker_publisher.publish(marker)
            self.get_logger().info(f'Marqueur publié à ({self.current_position.x}, {self.current_position.y}) avec température {self.current_temperature}°C')

    def send_position_data(self):
        # Envoyer la position réelle au client (si connecté)
        if self.client_socket is not None and self.current_position is not None:
            position = (self.current_position.x, self.current_position.y)
            message = f'Position: {position[0]:.2f}, {position[1]:.2f}'
            try:
                self.client_socket.send(message.encode())
                self.get_logger().info(f'Donnée de position envoyée: {message}')
            except socket.error as e:
                self.get_logger().error(f'Erreur lors de l\'envoi de la position: {e}')
        else:
            self.get_logger().warn('Aucune position ou connexion disponible')

    def destroy_node(self):
        # Nettoyage avant la destruction du node
        if self.client_socket is not None:
            self.client_socket.close()
            self.get_logger().info('Connexion au FiPy fermée')
        if self.server_socket is not None:
            self.server_socket.close()
            self.get_logger().info('Serveur TCP fermé')
        if self.db_connection is not None:
            self.db_connection.close()
            self.get_logger().info('Connexion à la base de données fermée')
        super().destroy_node()

def main(args=None):
    rclpy.init(args=args)
    node = TcpSenderReceiverNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
