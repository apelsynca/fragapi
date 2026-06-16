import json
from base64 import b64encode
from datetime import datetime
from hashlib import sha256
from time import time
from typing import Annotated, Self

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)
from pydantic import BaseModel, ConfigDict, Field
from ton_core import Address, Cell, PrivateKey, PublicKey, StateInit
from tonutils.contracts import BaseWallet


class TonConnectData(BaseModel):
    account: dict
    device: dict
    proof: dict


class TonConnectMessage(BaseModel):
    address: str
    amount: int
    payload: str | None = None

    def get_payload_cell(self) -> Cell:
        if self.payload is None:
            raise ValueError("TonConnectMessage has no payload.")

        padded_payload = self.payload + "=" * (-len(self.payload) % 4)
        return Cell.one_from_boc(padded_payload)


class TonConnectTransaction(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    valid_until: Annotated[datetime, Field(alias="validUntil")]
    from_address: Annotated[str, Field(alias="from")]  # NOT user friendly
    messages: list[TonConnectMessage]


class TonConnect:
    def __init__(
        self,
        tc_domain: str,
        state_init: StateInit,
        public_key: PublicKey,
        private_key: PrivateKey,
        address: Address,
    ) -> None:
        self.state_init = state_init
        self.public_key = public_key
        self.private_key = private_key
        self.wallet_address = address

        self.tc_domain = tc_domain

    @classmethod
    def from_wallet(cls, wallet: BaseWallet, tc_domain: str) -> Self:
        assert wallet.state_init
        assert wallet.public_key
        assert wallet.private_key

        return cls(
            tc_domain=tc_domain,
            state_init=wallet.state_init,
            public_key=wallet.public_key,
            private_key=wallet.private_key,
            address=wallet.address,
        )

    def get_connect_json_data(self, ton_proof_payload: str) -> dict[str, str]:
        connect_data = self.get_connect_data(ton_proof_payload=ton_proof_payload)

        return {
            "account": json.dumps(connect_data.account, separators=(",", ":")),
            "device": json.dumps(connect_data.device, separators=(",", ":")),
            "proof": json.dumps(connect_data.proof, separators=(",", ":")),
        }

    def get_connect_data(self, ton_proof_payload: str) -> TonConnectData:
        return TonConnectData(
            account=self.get_account(),
            device=self.get_device(),
            proof=self.get_proof(payload_hex=ton_proof_payload),
        )

    def get_account(self) -> dict:
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

    def get_device(self) -> dict:
        return {
            "platform": "iphone",
            "maxProtocolVersion": 2,
            "appVersion": "26.04.2",
            "features": [
                "SendTransaction",
                {"name": "SendTransaction", "maxMessages": 255},
                {"types": ["text", "binary", "cell"], "name": "SignData"},
            ],
            "appName": "Tonkeeper",
        }

    def get_proof(self, payload_hex: str) -> dict:
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
            "payload": payload_hex,
            "signature": b64encode(signature).decode(),
        }
