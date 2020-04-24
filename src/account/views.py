# from . import *
# def login(request):
#     if request.user.is_authenticated:
#         return redirect('home')
#
#     if request.POST:
#         form = LoginForm(request.POST)
#         if form.is_valid():
#             cred = form.cleaned_data
#             username = cred['username']
#             password = cred['password']
#             user = auth.authenticate(request, username=username, password=password)
#             if user is not None:
#                 auth.login(request, user)
#                 return redirect('home')
#             else:
#                 messages.error(request, 'Username or Password maybe incorrect. Try again')
#     return render(request, 'account/login.html')
#
#
# def logout(request):
#     auth.logout(request)
#     return redirect('login')
#
#
# def home(request):
#     if request.user.is_authenticated:
#         return render(request, 'account/home.html')
#     return redirect('login')
#
#
# def sign_up(request):
#     if request.POST:
#         form = SignUpForm(request.POST)
#
#         if form.is_valid():
#             user_info = form.cleaned_data
#             username = user_info['username']
#             email = user_info['email']
#             password = user_info['password']
#             first_name = user_info['first_name']
#             last_name = user_info['last_name']
#             phone_number = user_info['phone_number']
#             age = user_info['age']
#
#             # validate email
#             if not validate_email(email):
#                 messages.error(request, 'This email is not valid')
#                 return redirect('sign_up')
#
#             # save the user info
#             if not (User.objects.filter(username=username).exists() or User.objects.filter(email='email').exists()):
#                 # create user and account
#                 user = User.objects.create_user(username=username, password=password, first_name=first_name,
#                                                 last_name=last_name, email=email)
#                 user.save()
#                 account = Account.objects.create(user=user, age=age, phone_number=phone_number)
#
#                 # log them in
#                 cred = auth.authenticate(request, username=username, password=password)
#                 auth.login(request, cred)
#
#                 return redirect('home')
#             else:
#                 messages.error(request, 'Looks like this username or email already exists')
#
#
#     return render(request, 'account/sign_up.html')
#
#
# # def get_client_ip(request):
# #     x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
# #     if x_forwarded_for:
# #         ip = x_forwarded_for.split(',')[0]
# #     else:
# #         ip = request.META.get('REMOTE_ADDR')
# #     return ip
#
#
# # class FileProcessor(object):
# # 	def process(file_path):
# # 		import os
# # 		import csv
# # 		lines = []
# # 		if os.path.isfile(file_path):
# # 			with open(file_path) as f_in:
# # 				reader = csv.reader(f_in)
# # 				for row in reader:
# # 					lines.append(row)
# #
# # 		if lines:
# # 			with open('/tmp/foo.txt', 'w') as f_out:
# # 				for line in lines:
# # 					f_out.write("%s\n" % lines)
# #
# # 		return
#
#
# # def upload(request):
# #
# #     # any row that throws an error WILL BE SKIP PERIOD
# #
# #     if request.POST and request.FILES:
# #         csv_file = request.FILES['file']
# #         if not str(csv_file.name).endswith('.csv'):
# #             messages.error(request, 'File must be CSV')
# #             return redirect('upload')
# #
# #         # restrict upload if account is inactive
# #         if not request.user.account.active:
# #             messages.error(request, 'You are not allow to upload file. Contact support to update your account')
# #             return render(request, 'account/upload.html')
# #
# #         duplicates = CallerId.objects.filter(account=request.user.account)
# #
# #         csv_line = csv_file.readline().decode('ISO-8859-1')
# #         while csv_line:
# #             line = csv_line.strip().split(',')
# #             data = dict()
# #             try:
# #                 #sanitize remove non ascii
# #                 data['phone_number'] = int(clean_number(line[0]))
# #                 data['label'] = line[1].strip().encode('ascii',errors='ignore').decode()
# #                 data['account'] = request.user.account.id
# #             except:
# #                 csv_line = csv_file.readline().decode('ISO-8859-1')
# #                 continue
# #
# #             dup_checked = duplicates.filter(phone_number=data['phone_number']).first()
# #             if dup_checked:
# #                 # if cid exist whether 'delete' or not we update it stat and show
# #                 #reputation_obj = CallerIdReputation.objects.filter(caller_id=dup_checked).first()
# #                 dup_checked.deleted = False
# #                 dup_checked.date_modified = django_timezone.now()
# #                 dup_checked.label = data['label']
# #                 #if reputation_obj:
# #                 #	reputation_obj.date_modified = django_timezone.now()
# #                 #	reputation_obj.save()
# #                 dup_checked.save()
# #                 # update the reputation
# #                 generate_reputation_obj(dup_checked, request.user.account)
# #             else:
# #                 try:
# #                     form = UploadForm(data)
# #                     if form.is_valid():
# #                         obj = form.save()
# #                         generate_reputation_obj(obj, request.user.account)
# #                 except:
# #                     pass
# #
# #             csv_line = csv_file.readline().decode('ISO-8859-1')
# #         return redirect('home')
# #
# #
# #     #
# #     # 	# # todo start carrot task here comment out blow
# #     # 	# worker = Worker(name=csv_file.name)
# #     # 	# worker.description = 'Used for processig callerid from csv upload'
# #     # 	# worker.save()
# #     # 		#Task.objects.create(kallable='src.account.utils.CSVParser.caller_id_upload', args=[request])
# #     #
# #     #
# #     # 	file_path = '/tmp/upload.txt'
# #     #
# #     # 	with open(file_path, 'wb') as f_out:
# #     # 		for chunk in csv_file.chunks():
# #     # 			f_out.write(chunk)
# #     #
# #     # 	Task.objects.create(kallable='account.views.FileProcessor.process', args=[file_path])
# #     #
# #
# #     if request.POST and not request.FILES:
# #         # restrict upload if account is inactive
# #         if not request.user.account.active:
# #             messages.error(request, 'You are not allow to upload file. Contact support to update your account')
# #             return render(request, 'account/upload.html')
# #
# #         phone_numbers = request.POST.get('phone_numbers', None)
# #         labels = request.POST.get('labels', None)
# #
# #         if labels is None or phone_numbers is None:
# #             return render(request, 'account/upload.html')
# #
# #         phone_numbers = str(phone_numbers).split(',')
# #         labels = str(labels).split(',')
# #
# #         if len(phone_numbers) != len(labels):
# #             return render(request, 'account/upload.html')
# #
# #         duplicates = CallerId.objects.filter(account=request.user.account)
# #         for i in range(len(phone_numbers)):
# #             data = dict()
# #
# #             try:
# #                 #sanitize remove non ascii
# #                 data['phone_number'] = int(clean_number(phone_numbers[i]))
# #                 data['label'] = labels[i].strip().encode('ascii',errors='ignore').decode()
# #                 data['account'] = request.user.account.id
# #             except:
# #                 continue
# #
# #             dup_checked = duplicates.filter(phone_number=data['phone_number']).first()
# #
# #             if dup_checked:
# #                 # if cid exist whether 'delete' or not we update it stat and show
# #                 #reputation_obj = CallerIdReputation.objects.filter(caller_id=dup_checked).first()
# #                 dup_checked.deleted = False
# #                 dup_checked.date_modified = django_timezone.now()
# #                 dup_checked.label = data['label']
# #                 #if reputation_obj:
# #                 #	reputation_obj.date_modified = django_timezone.now()
# #                 #	reputation_obj.save()
# #                 dup_checked.save()
# #                 # update the reputation
# #                 generate_reputation_obj(dup_checked, request.user.account)
# #             else:
# #                 try:
# #                     form = UploadForm(data)
# #                     if form.is_valid():
# #                         obj = form.save()
# #                         generate_reputation_obj(obj, request.user.account)
# #                 except:
# #                     pass
# #         return redirect('home')
# #     # 	else:
# #     # 		try:
# #     # 			worker = Worker(name='manual upload')
# #     # 			worker.description = 'Used for processig callerid from csv upload -%s' % request.user.account
# #     # 			worker.save()
# #     # 			Task.objects.create(kallable='account.utils.CSVParser.caller_id_upload2', args=[request,phone_numbers,labels],worker=worker)
# #     # 		except:
# #     # 			worker.delete()
# #     # 			messages.error(request, 'ERROR uploading list')
# #     #
# #     #
# #     #
# #     return render(request, 'account/upload.html')
# #
#
