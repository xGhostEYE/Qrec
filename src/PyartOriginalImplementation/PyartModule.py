import os
import re
import sys
import PyartDataflowExtraction as DataFlow

'''
	This contents of this file was modified and ported from Python API Recommendation in Real-Time: https://github.com/PYART0/PyART-demo
'''


def get_bank(line):
	ip=0
	for ip in range(0,len(line)):
		if line[ip]!=' ':
			break
	return (line[:ip],ip)

def get_caller(rec):
	nrec=re.sub('\(.*\)','',rec)
	pindex=nrec.rfind('.')
	return nrec[:pindex]

def get_recs(rec):
	return

def get_callers(rec):
	nrec=re.sub('\(.*\)','',rec)
	pindex=nrec.rfind('.')
	return nrec[:pindex]

def get_callee(rec):
	nrec=re.sub('\(.*\)','',rec)
	pindex=nrec.rfind('.')
	return nrec[pindex+1:],rec[pindex+1:]

def check(newcontext):
	ls=newcontext.split('\n')
	i=0
	for i in range(len(ls)-1,-1,-1):
		if ls[i].strip().startswith('def'):
			break
	nc=''
	for j in range(i,len(ls)):
		nc+=ls[j]+'\n'
	#nc=newcontext
	#print(nc)
	nc=re.sub('\'[\\\[\]\(\)\{\}A-Za-z0-9_\,\:]+\'','',nc)
	nc=re.sub('\"[\\\[\]\(\)\{\}A-Za-z0-9_\,\:]+\"','',nc)

	lk=nc.count('(')
	rk=nc.count(')')
	ll=nc.count('[')
	rl=nc.count(']')
	ld=nc.count('{')
	rd=nc.count('}')
	kc=lk-rk
	lc=ll-rl
	dc=ld-rd
	addc=''
	#print(kc,lc,dc)
	if kc==lc==dc==0:
		return newcontext
	else:
		ks=''
		#print(nc)
		for i in range(0,len(nc)):
			c=nc[i]
			if re.match('[\(\)\[\]\{\}]',c):
				ks+=c				
		#print(ks)
		while('{}' in ks or '[]' in ks or '()' in ks):
			while '()' in ks:
				ks=re.sub('\[\]','',ks)
				ks=re.sub('\{\}','',ks)
				ks=re.sub('\(\)','',ks)
			while '[]' in ks:
				ks=re.sub('\{\}','',ks)
				ks=re.sub('\(\)','',ks)
				ks=re.sub('\[\]','',ks)
			while '{}' in ks:
				ks=re.sub('\[\]','',ks)
				ks=re.sub('\(\)','',ks)
				ks=re.sub('\{\}','',ks)
		#print(ks)
		for i in range(len(ks)-1,-1,-1):
			if ks[i]=='(':
				addc+=')'
			elif ks[i]=='[':
				addc+=']'
			else:
				addc+='}'
		#print(newcontext)
		#sys.exit(0)
		#x=re.sub('return ','',newcontext+addc)
		return newcontext+addc
		

def get_type(finalc,file):

	lindex=file.rfind('/')
	tmp=file[:lindex]+'/tmp.py'

	with open(tmp,'w+') as f:
		f.write(finalc)
	#with open(tmp2,'w+') as f2:
		#f2.write(finalc)
	try:
		#os.system('pytype '+tmp)
		os.system('pytype '+tmp+' > log.txt')
		#os.system('rm '+tmp)
	except Exception:
		sys.exit()
	with open('log.txt') as f:
		lines=f.readlines()
	vtype='None'
	for line in lines:
		if '[reveal-type]' in line:
			tp=line.split(':')[1]
			vtype=re.sub('\[reveal\-type\]','',tp)
			#print(vtype)
			break
		#if '[python-compiler-error]' in line:
			#sys.exit()

	# global Nonenum,Anynum,OKnum
	# if vtype=='None':
	# 	#print(tmp)
	# 	#sys.exit()
	# 	Nonenum+=1
	# elif vtype=='Any' or vtype=='nothing':
	# 	Anynum+=1
	# else:
	# 	OKnum+=1
	return vtype


def get_bank(line):
	ip=0
	for ip in range(0,len(line)):
		if line[ip]!=' ':
			break
	return (line[:ip],ip)

def check_try(code,trycache):
	#print(trycache)
	ret=code
	#l=sorted(trycache)
	#print(l)
	for i in range(len(trycache)-1,-1,-1):
		ret+='\n'+trycache[i][0]+'except Exception:\n'+trycache[i][0]+'	'+'pass'
	return ret

def extract_data_pyart_original(rawfile, changed_lines_dict):
	with open(rawfile) as f:
		lines=f.readlines()
		#print(lines)
	precode=''
	trynum=0
	trycache=[]
	kflag=0
	lno=0
	#s=''
	comment_flag=0
	calls=[]

	for line in lines:
		#print(line)
		lno+=1
		if line.strip().startswith('#'):
			continue
		if re.match('[bru]*\'\'\'$',line.strip()) or re.match('[bru]*\"\"\"$',line.strip()):
			if comment_flag==0:
				comment_flag=1
			else:
				comment_flag=0
			continue
		elif (re.match('[bru]*\'\'\'',line.strip()) or re.match('[bru]*\"\"\"',line.strip())) and (re.match('.*[bru]*\'\'\'$',line.strip()) or re.match('.*[bru]*\"\"\"$',line.strip())):
			continue
		elif re.match('[bru]*\'\'\'',line.strip()) or re.match('[bru]*\"\"\"',line.strip()) or re.match('.*[bru]*\'\'\'$',line.strip()) or re.match('.*[bru]*\"\"\"$',line.strip()):
			if comment_flag==0:
				comment_flag=1
			else:
				comment_flag=0
			continue
		if comment_flag==1:
			continue
				
		if 'try:' in line:
			trynum+=1
			trycache.append(get_bank(line))
		elif trynum>0 and ('except' in line or 'finally:' in line):
			(bank,lenth)=get_bank(line)
			for i in range(len(trycache)-1,-1,-1):
				if trycache[i][1]==lenth:
					trynum-=1
					del trycache[i]
		
		recobj=re.findall('[a-zA-Z0-9_\.\[\]]+\.[a-zA-Z0-9\_]+\(.*\)',line)
		#print(recobj)
		if len(recobj)==0:
			precode+=line
			continue

		rec=recobj[0]
		caller_and_callee_info_dict = get_caller_and_callee_info(rec)
		
		for caller, callee_info in caller_and_callee_info_dict.items():
			if caller.startswith('['):
				caller=caller[1:]
			
			callee,rcallee=callee_info

			# if callee.startswith('_') or re.match('[A-Z0-9_]+$',callee) or callee.strip()=='_':
			# 	# precode+=line
			# 	continue
			# cp=caller+'.'+callee
			# if cp in calls:
			# 	# precode+=line
			# 	continue
			# else:
			# 	calls.append(cp) 

			i=0
			latest_line=line.replace(rcallee,'unknown_api()')
			#print('NOTE!',latest_line)
			
			tpp=precode.strip()
			if tpp.endswith(','):

				newcontext=tpp[:-1]
				finalc=check(newcontext)
				#print(finalc)
				current_context=finalc+'\n'+latest_line

				prelast=precode.strip().split('\n')[-1]
				for i in range(0,len(prelast)):
					if prelast[i]!=' ':
						break
				finalc+='\n'+line[:i-4]+'reveal_type('+caller+')'
				
			elif tpp.endswith('(') or tpp.endswith('{') or tpp.endswith('['):
				
				newcontext=tpp
				finalc=check(newcontext)
				current_context=finalc+'\n'+latest_line
				
				#print(finalc)
				prelast=precode.strip().split('\n')[-1]
				for i in range(0,len(prelast)):
					if prelast[i]!=' ':
						break
				finalc+='\n'+line[:i]+'reveal_type('+caller+')'

			else:
				for i in range(0,len(line)):
					if line[i]!=' ':
						break
				#print(i)
				#print(line)
				newcontext=tpp
				finalc=check(newcontext)
				finalc+='\n'+line[:i]+'reveal_type('+caller+')'
				current_context=precode+latest_line
		
			if len(trycache)>0:
				finalc=check_try(finalc,trycache)
			
			if re.match('[A-Z]+[A-Za-z]+',callee) or callee.startswith('_'):
				print('CONSTRUCTOR,IGNORE')
				precode+=line
				continue
		
			current_dataflow=DataFlow.get_current_dataflow(current_context,caller)
			if len(current_dataflow)==0:
				precode+=line
				continue
				
				# maxflow=max(current_dataflow,key=len)
		
def recheck2(l):
	line=l
	line=re.sub('return ','',line)
	line=re.sub('\[.*\]','',line)
	line=re.sub('\(.*\)','',line)
	line=re.sub('\{.*\}','',line)
	line=re.sub('\+\=','=',line)
	#line=re.sub(' ','',line)
	line=re.sub('r\'.*\'\,*\s*','',line)
	line=re.sub('b\'.*\'\,*\s*','',line)
	line=re.sub('rb\'.*\'\,*\s*','',line)
	line=re.sub('f\'.*\'\,*\s*','',line)
	line=re.sub('\'.*\'\,*\s*','',line)
	line=re.sub('\".*\"\,*\s*','',line)
	line=re.sub('r\".*\"\,*\s*','',line)
	line=re.sub('b\".*\"\,*\s*','',line)
	line=re.sub('rb\".*\"\,*\s*','',line)
	line=re.sub('f\".*\"\,*\s*','',line)
	#line=recheck(line)
	line=line.strip()
	return line

def recheck(l):
	line=l
	line=re.sub('return ','',line)
	line=re.sub('\[\'.*\'\]','',line)
	line=re.sub('\[\".*\"\]','',line)
	line=re.sub('\(\'.*\'\)','',line)
	line=re.sub('\(\".*\"\)','',line)
	line=re.sub('\[[0-9\.\-\s\:]+\]','',line)
	line=re.sub('\([0-9\.\-\s\:]+\)','',line)
	line=re.sub('\{[0-9\.\-\s\:]+\}','',line)
	line=re.sub('\[.*[\+\:]+.*\]','',line)
	line=re.sub('\+\=','=',line)
	#line=re.sub(' ','',line)
	line=re.sub('r\'.*\'\,*\s*','',line)
	line=re.sub('b\'.*\'\,*\s*','',line)
	line=re.sub('rb\'.*\'\,*\s*','',line)
	line=re.sub('f\'.*\'\,*\s*','',line)
	line=re.sub('\'.*\'\,*\s*','',line)
	line=re.sub('\".*\"\,*\s*','',line)
	line=re.sub('r\".*\"\,*\s*','',line)
	line=re.sub('b\".*\"\,*\s*','',line)
	line=re.sub('rb\".*\"\,*\s*','',line)
	line=re.sub('f\".*\"\,*\s*','',line)
	line=re.sub('\(\)','',line)
	line=re.sub('\{\}','',line)
	line=re.sub('\[\]','',line)
	#line=recheck(line)
	line=line.strip()
	return line	
