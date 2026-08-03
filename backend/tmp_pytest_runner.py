import os
import pytest

os.chdir(r'd:/medigenie/backend')
rc = pytest.main(['-q', '--disable-warnings'])
print('RC:', rc)
