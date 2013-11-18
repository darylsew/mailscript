import email, imaplib, os, time
from printer import default_printer

detach_dir = '.' # directory where to save attachments (default: current)
user = 'darylprint@gmail.com' #Email to send print reqs to
pwd = open('config.cred').readline().strip() #Your password location
exts = ['pdf', 'docx', 'txt','doc', 'odt', 'dvi'] #List of approved exentions

# connecting to the gmail imap server
m = imaplib.IMAP4_SSL("imap.gmail.com") #Edit this line w/ your imap server of chocie
m.login(user,pwd)
wl = [i.strip for i in open("whitelist.cred").readlines()]

while True:
    time.sleep(1)
    m.select("INBOX") 	# here you a can choose a mail box like INBOX instead
    			# use m.list() to get all the mailboxes
    toprint = [i for i in os.listdir('.') if i.split('.')[-1] in exts]
    if len(toprint) != 0:
        default_printer(toprint[0])
        time.sleep(30)
        os.remove(toprint[0])
    
    resp, items = m.search(None, 'UNSEEN') 
    items = items[0].split() # Getting the mails ID
    
    for emailid in items:
        resp, data = m.fetch(emailid, "(RFC822)") #(RFC822) gives full contents of mail
        email_body = data[0][1] # Getting the mail content
        mail = email.message_from_string(email_body) # Parse email to String
    
	#Checks to see if the recieved email is in the whitelist
    	if not mail["From"] in wl:
	    print "Recieved email from non-whitelisted user: "+mail["From"]
	    m.store(mail, '+FLAGS', '\\Deleted')
	    m.expunge
	    continue

        #Check if any attachments at all
        if mail.get_content_maintype() != 'multipart':
    	    continue

        #print 'yo i got attachments'
        if mail["Subject"].lower() == 'print':
    
            #print "["+mail["From"]+"] :" + mail["Subject"]
    
            for part in mail.walk():
                # multipart are just containers, so we skip them
                if part.get_content_maintype() == 'multipart':
                    continue
    
                # is this part an attachment ?
                if part.get('Content-Disposition') is None:
                    continue
    
                filename = part.get_filename()
                counter = 1
    
                # if there is no filename, we create one with a counter to avoid duplicates
                if not filename:
                    filename = 'part-%03d%s' % (counter, 'bin')
                    counter += 1
    
                att_path = os.path.join(detach_dir, filename)
    
                #Check if its already there
                if not os.path.isfile(att_path) :
                    # finally write the stuff
                    fp = open(att_path, 'wb')
                    fp.write(part.get_payload(decode=True))
                    fp.close()

		m.store(mail, '+FLAGS', '\\Deleted')
		m.expunge()
	    
