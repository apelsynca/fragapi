from base64 import b64encode
from hashlib import sha256
from time import time

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)
from tonutils.contracts import BaseWallet


class TonConnect:
    def __init__(self, wallet: BaseWallet, tc_domain: str) -> None:
        assert wallet.state_init is not None
        assert wallet.public_key is not None
        assert wallet.private_key is not None

        self.state_init = wallet.state_init
        self.public_key = wallet.public_key
        self.private_key = wallet.private_key
        self.wallet_address = wallet.address

        self.tc_domain = tc_domain

    def get_account(self):
        wallet_state_init = self.state_init.serialize().to_boc()
        wallet_state_init_base64 = b64encode(wallet_state_init).decode()

        workchain = self.wallet_address.wc
        address_hash = self.wallet_address.hash_part

        return {
            "address": f"{workchain}:{address_hash.hex()}",
            "chain": "-239",
            "walletStateInit": wallet_state_init_base64,
            "publicKey": self.public_key.as_hex,
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
        workchain = self.wallet_address.wc
        address_hash = self.wallet_address.hash_part

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

        private_key = Ed25519PrivateKey.from_private_bytes(self.private_key.as_bytes)
        signature = private_key.sign(final_hash)

        public_key = Ed25519PublicKey.from_public_bytes(self.public_key.as_bytes)
        public_key.verify(signature, final_hash)

        return {
            "timestamp": timestamp,
            "domain": {"lengthBytes": len(domain_bytes), "value": self.tc_domain},
            "signature": b64encode(signature).decode(),
            "payload": payload_hex,
        }
