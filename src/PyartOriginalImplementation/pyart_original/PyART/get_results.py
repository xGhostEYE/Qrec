import json

def get_results(arr):
	top1=0
	top2=0
	top3=0
	top4=0
	top5=0
	top10=0
	top20=0
	for i in range(0,len(arr)):
		if arr[i]==1:
			top1+=1
			top2+=1
			top3+=1
			top4+=1
			top5+=1
			top10+=1
			top20+=1
		elif arr[i]==2:
			top2+=1
			top3+=1
			top4+=1
			top5+=1
			top10+=1
			top20+=1
		elif arr[i]==3:
			top3+=1
			top4+=1
			top5+=1
			top10+=1
			top20+=1
		elif arr[i]==4:
			top4+=1
			top5+=1
			top10+=1
			top20+=1
		elif arr[i]==5:
			top5+=1
			top10+=1
			top20+=1
		elif arr[i]<=10:
			top10+=1
			top20+=1
		elif arr[i]<=20:
			top20+=1
	top1=float(top1)
	top2=float(top2)
	top3=float(top3)
	top4=float(top4)
	top5=float(top5)
	top10=float(top10)
	top20=float(top20)
	lenth=float(len(arr))
	tp1=float(top1/lenth)
	tp2=float(top2/lenth)
	tp3=float(top3/lenth)
	tp4=float(top4/lenth)
	tp5=float(top5/lenth)
	tp10=float(top10/lenth)
	tp20=float(top20/lenth)
	rlen=len(arr)
	maps=0.0
	for i in range(0,rlen):
		maps+=float(1.0/float(arr[i]))
	maps=float(maps/float(rlen))
	#print("Top-k:",top1,top2,top3,top4,top5,top10,top20,len(arr))
	print("Top-k:",tp1,tp2,tp3,tp4,tp5,tp10,tp20,maps)
	print("mrr:",maps)


'''
apirecfile='apirec_cornice_results.json'

with open(apirecfile) as f:
	apirecrets=json.load(f)
	
ranks=[]

for k,v in apirecrets.items():
	for i in v:
		ranks.append(int(i.split('#')[1]))
'''
def run(pranks, pinranks):

	print("results for pranks")
	with open(pranks) as file:
		lines = [int(line.rstrip()) for line in file]
		get_results(lines)

	print("results for pinranks")
	with open(pinranks) as file:
		lines = [int(line.rstrip()) for line in file]
		get_results(lines)
