"""Views, one for each Insta485 page."""
from insta485.views.index import show_index
from insta485.views.explore import show_explore
from insta485.views.following import show_following
from insta485.views.followers import show_followers
from insta485.views.user import show_user
from insta485.views.post import show_post
from insta485.views.post_requests import edit_comments
from insta485.views.login import check_login_status
from insta485.views.accounts_requests import account
from insta485.views.logout import logout
from insta485.views.create import create_prelim
from insta485.views.edit import create_edit
from insta485.views.delete import delete_prelim
from insta485.views.password import show_pass
# from insta485.views.user_requests import edit
