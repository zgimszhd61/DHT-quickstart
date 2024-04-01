# import libtorrent as lt
# import time
# import binascii

# def fetch_metadata(info_hash_str):
#     # 检查info-hash格式并转换为十六进制字符串（如果需要）
#     if isinstance(info_hash_str, bytes):
#         info_hash_str = binascii.hexlify(info_hash_str).decode('ascii')
#     elif not isinstance(info_hash_str, str) or len(info_hash_str) != 40:
#         raise ValueError("info-hash must be a 40-character hexadecimal string")

#     # 初始化会话
#     ses = lt.session({'listen_interfaces': '0.0.0.0:6881'})
#     ses.add_dht_router("router.utorrent.com", 6881)
#     ses.add_dht_router("router.bittorrent.com", 6881)
#     ses.add_dht_router("dht.transmissionbt.com", 6881)
#     ses.start_dht()

#     # 创建磁力链接
#     magnet_uri = f"magnet:?xt=urn:btih:{info_hash_str}"

#     # 添加磁力链接到会话
#     params = {
#         'save_path': './',
#         'storage_mode': lt.storage_mode_t.storage_mode_sparse,
#         'auto_managed': True,
#     }
#     handle = lt.add_magnet_uri(ses, magnet_uri, params)

#     print('Downloading metadata...')
#     # 等待元数据下载完成
#     while not handle.has_metadata():
#         time.sleep(1)

#     # 获取种子文件的元数据
#     torrent_info = handle.get_torrent_info()
#     files = torrent_info.files()
#     for file_index, file in enumerate(files):
#         print(f"File {file_index}: {file.path}, size: {file.size}")

# # 示例infohash
# info_hash = ''
# fetch_metadata(info_hash)

import socket
import bencodepy
from hashlib import sha1
import random
import os

def random_node_id():
    return sha1(os.urandom(20)).digest()

def send_find_node_request(sock, address):
    transaction_id = os.urandom(2)
    node_id = random_node_id()
    payload = {
        't': transaction_id,
        'y': 'q',
        'q': 'find_node',
        'a': {
            'id': node_id,
            'target': random_node_id()
        }
    }
    sock.sendto(bencodepy.encode(payload), address)

def handle_message(sock, data, address):
    try:
        message = bencodepy.decode(data)
        if b"y" in message:
            if message[b"y"] == b"q":
                query_type = message[b"q"]
                if query_type == b"get_peers":
                    info_hash = message[b"a"][b"info_hash"]
                    print(f"Received get_peers for info_hash: {info_hash.hex()}")
                elif query_type == b"announce_peer":
                    info_hash = message[b"a"][b"info_hash"]
                    print(f"Received announce_peer for info_hash: {info_hash.hex()}")
            elif message[b"y"] == b"r":
                if b"nodes" in message[b"r"]:
                    # 这里可以处理返回的节点信息
                    pass
    except Exception as e:
        print(f"Error handling message: {e}")

def start_dht_node(bind_ip, bind_port, bootstrap_address):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((bind_ip, bind_port))
    print(f"DHT Node running on {bind_ip}:{bind_port}")

    # 发送find_node请求到引导节点，开始加入DHT网络
    send_find_node_request(sock, bootstrap_address)

    while True:
        data, addr = sock.recvfrom(65536)
        handle_message(sock, data, addr)

if __name__ == "__main__":
    # 引导节点地址，这里使用了BitTorrent的引导节点之一
    bootstrap_address = ("router.utorrent.com", 6881)
    start_dht_node("0.0.0.0", 6881, bootstrap_address)
