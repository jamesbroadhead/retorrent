def rapidline_to_rapidlink(rapidline):
	if 'DONE:' in rapidline:
		rapidlink = rapidline.split('DONE:')[-1].lstrip().rstrip(' \n')
	else:
		rapidlink = rapidline

	return rapidlink.strip(' \n')

def rapidline_to_filename(rapidline):
	rapidlink = rapidline_to_rapidlink(rapidline)
	return rapidlink_to_filename(rapidlink)

def rapidlink_to_filename(rapidlink):
	if not can_predict_filename_from_rapidlink(rapidlink):
		return ''
	
	filename = rapidlink.split('/')[-1].rstrip(' \n')
	
	rtrim_these = [ '.html' ]

	for item in rtrim_these:
		if filename.endswith(item):
			filename = filename[0:-len(item)]
	
	filename = filename.strip()
	
	#DEBUG
	#print 'rapidlink_to_filename: ' + rapidlink + ' -> ' + filename

	return filename
 
def filename_to_rapidlink(filename,listfilename):
	rapidline = filename_to_rapidline(filename,listfilename)
	return rapidline_to_rapidlink(rapidline)

def filename_to_rapidline(filename,listfilename):
	listfile = open(listfilename)

	for line in listfile.readlines():
		if rapidline_to_filename(line) == filename:
			return line
	
	listfile.close()	
	return ''


def can_predict_filename_from_rapidlink(rapidlink):
	if 'megaupload' in rapidlink:
		return False
	return True


