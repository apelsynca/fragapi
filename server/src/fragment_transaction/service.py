from sqlalchemy.ext.asyncio import AsyncSession

from src.fragment_transaction.repository import FragmentTransactionRepository
from src.models import FragmentTransaction, Transaction, User
from src.models.fragment_transactions import FragmentTransactionReason


class FragmentTransactionService:
    async def create(
        self,
        session: AsyncSession,
        user: User,
        amount: float,
        recipient: str,
        username: str,
        transaction: Transaction,
        reason: FragmentTransactionReason,
    ) -> FragmentTransaction:
        frag_trans = FragmentTransaction(
            user=user,
            amount=amount,
            recipient=recipient,
            username=username,
            transaction=transaction,
            reason=reason,
        )

        repository = FragmentTransactionRepository.from_session(session)

        return await repository.create(frag_trans)


fragment_transaction = FragmentTransactionService()
