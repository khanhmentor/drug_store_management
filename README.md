# Restaurant Management - Order Management System

## Do all the following to run the project:

- ### `py manage.py makemigrations order_management` (`python3 manage.py makemigrations order_management`)
- ### `py manage.py migrate` (`python3 manage.py migrate`)
- ### `py manage.py shell` (`python3 manage.py shell`)
- ### type the below in shell:

#### `from order_management.models import CategoryType, CategoryItem, User, Status`

#### `a = {'admin': ['(336) 957-2666', '671 Oak Ridge Church Rd Hays, North Carolina(NC)'], 'supplier': ['(503) 468-0322', '1 3rd St Astoria, Oregon(OR)'], 'supplier1': ['(248) 627-6468', '1275 Granger Rd Ortonville, Michigan(MI)'], 'customer': ['(856) 310-0296', '171 Carlisle Rd Audubon, New Jersey(NJ)'], 'customer1': ['(918) 341-5699', '18705 Timberlake Dr Claremore, Oklahoma(OK)']}`

#### `for i in a:`
####    `user = User(username=i, password=i, name=i, email=i+'@gmail.com', phone=a[i][0], address=a[i][1])`
####    `user.save()`

#### `a = ['waiting', 'placed', 'forwarded', 'confirmed', 'processed', 'shipped', 'received', 'delivering', 'delivered', 'completed', 'denied']`

#### `for i in a:`
####    `status = Status(name=i)`
####    `status.save()`

- ### `py manage.py runserver` (`python3 manage.py runserver`)
- ### the site is now listening at [http://localhost:8000](http://localhost:8000)
- ### use these pre-established accounts for authentication or you can modify the code above to create any account you want

## If you have any issue with session use the following code in shell to modify or event delete existing session:

#### `from django.contrib.sessions.models import Session`

#### `Session.objects.all()`: to get all existing session and modify them (`.delete()` to remove them)