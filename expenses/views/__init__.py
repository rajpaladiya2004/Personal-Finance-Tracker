"""Views grouped by feature. Re-exported so ``expenses.views.<name>`` keeps working."""

from .auth import delete_account, home, register
from .categories import add_category, category_list
from .dashboard import dashboard
from .notifications import notifications
from .pages import about_us, contact_us, faq, help_support, privacy_policy, terms_conditions
from .profile import profile
from .transactions import add_transaction, delete_transaction, edit_transaction, transaction_list

__all__ = [
    'about_us', 'add_category', 'add_transaction', 'category_list', 'contact_us',
    'dashboard', 'delete_account', 'delete_transaction', 'edit_transaction', 'faq',
    'help_support', 'home', 'notifications', 'privacy_policy', 'profile', 'register',
    'terms_conditions', 'transaction_list',
]
