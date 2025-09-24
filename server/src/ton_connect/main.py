from base64 import b64encode
from hashlib import sha256
from time import time

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)

from src.ton_wallet import wallet


class TonConnect:
    def __init__(self, tc_domain: str) -> None:
        self.tc_domain = tc_domain

    def get_account(self):
        wallet_state_init = wallet.state_init.serialize().to_boc()
        wallet_state_init_base64 = b64encode(wallet_state_init).decode()

        workchain = wallet.address.wc
        address_hash = wallet.address.hash_part

        return {
            "address": f"{workchain}:{address_hash.hex()}",
            "chain": "-239",
            "walletStateInit": wallet_state_init_base64,
            "publicKey": wallet.public_key.hex(),
        }

    def get_device(self):
        return {
            "appVersion": "5.2.9",
            "platform": "iphone",
            "maxProtocolVersion": 2,
            "features": [
                "SendTransaction",
                {"name": "SendTransaction", "maxMessages": 255},
                "SignData",
                {"name": "SignData", "types": ["text", "binary", "cell"]},
            ],
            "appName": "Tonkeeper",
        }

    def get_proof(self, payload_hex: str):
        workchain = wallet.address.wc
        address_hash = wallet.address.hash_part

        timestamp = int(time())
        domain_bytes = self.tc_domain.encode("utf-8")

        message = (
            b"ton-proof-item-v2/"
            + workchain.to_bytes(4, "little")
            + address_hash
            + len(domain_bytes).to_bytes(4, "little")
            + domain_bytes
            + timestamp.to_bytes(8, "little")
            + payload_hex.encode()
        )

        signature_message = b"\xff\xffton-connect" + sha256(message).digest()
        final_hash = sha256(signature_message).digest()

        private_key = Ed25519PrivateKey.from_private_bytes(wallet.private_key[:32])
        signature = private_key.sign(final_hash)

        public_key = Ed25519PublicKey.from_public_bytes(wallet.public_key)
        public_key.verify(signature, final_hash)

        return {
            "timestamp": timestamp,
            "domain": {"lengthBytes": len(domain_bytes), "value": self.tc_domain},
            "signature": b64encode(signature).decode(),
            "payload": payload_hex,
        }
