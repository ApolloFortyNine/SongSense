import os
import os.path

package_dir = os.path.dirname(__file__)
git_dir = os.path.normpath(os.path.join(package_dir, os.pardir, os.pardir))
path = os.path.join(git_dir, '.git')