import time
import re
import threading
import sys
import urllib.request
import requests
import os

class threaddown:
	'''
	#ctrl+f快速定位
	初始线程常数
	index网址整理方式
	list_f_name简介
	[0]存储请求地址
	*>1
	[*]为文件名编号#请求索引
	创建好之后文件会被保存在index_b.txt
	'''
	add_thread=10
	#系统同时存在的线程最大数
	max_thread=200
	#request 子线程认定全部死亡时间设置
	timeout_max=40	#时间上限

	#ipwork='47.106.59.75:3128'

	#文件合并
	def addf(self,f_name):
		'''没有ffmepeg可以用cmd操作
		有概率合成的文件顺序不对，看操作系统的文件管理方式
		#os.system("copy /b "+f_name+"*.ts "+f_name+'.mp4')
		#os.system("del "+f_name+"*.ts ")
		'''
		#ffmpeg -f concat -safe 0 -i fflist.txt -c copy output.mp4
		time.sleep(1)
		#print("ffmpeg -f concat -safe 0 -i fflist.txt -c copy "+f_name+".mp4 &&del fflist.txt")
		key1=1
		key2=3
		while key1>0 and key2>0:
			try:
				#ffmpeg -allowed_extensions ALL -i 冰菓1.m3u8 -c copy out.mp4
				#https://blog.csdn.net/weixin_41624645/article/details/95939510
				stros=os.system("ffmpeg -allowed_extensions ALL -i "+f_name+".m3u8 "+"-c copy "+f_name+".mp4")
				if stros==0:
					#合并成功，删除无用存档文件
					os.system("del "+f_name+"*.ts")
					os.system("del "+f_name)
					os.system("del "+f_name+"_b")
					os.system("del "+f_name+"*.m3u8")
					os.system("del "+f_name+"存档.txt")
					key1=0
			except:
				key2=key2-1
				print("合成出错"+f_name+'次数'+str(key2))
				time.sleep(1)
		#os.system("del "+f_name+"*.ts ")
		#ffmpeg -f concat -safe 0 -i fflist.txt -c copy output.mp4


	#下载m3u8的index文件(网址，保存文件名字)
	def down_m3u8(self,m3u8_add,f_name):
		try:
			headers={
			'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'
			#,'Referer':net_add
			}
			#proxies={'https':'https://'+ipwork}
			#req=requests.get(m3u8_add,headers=headers,proxies=proxies)
			req=requests.get(m3u8_add,headers=headers)
			f=open(f_name,'w')
			#print(req.text)
			f.write(req.text)
			f.close()
			#print('成功'+m3u8_add)
			return 1
		except:
			print('失败'+m3u8_add)
			return 0

	#index网址整理
	def netadd_cat(self,netadd,wid1,wid2=0):
		'''参数简介+调用示例
		netadd	需要处理的网址
		wid1	index网址请求模式选择	1追加	0母网页
		wid2	index目录是否有‘/’	1删尾部‘/’
		#调用示例#追加模式
		if list_f_name[1].startswith('/'):
			netadd_cat(net_add,1,1)
		else :
			netadd_cat(net_add,1)
		'''
		netadd=re.sub(r'm3u8.+','',netadd)
		#追加模式，嵌套index是index子集，网址删除index.m3u8后追加
		if wid1==1:
			netadd=netadd[:netadd.rfind('/')+1]

		#母网页模式。在所有请求来自母网页
		elif wid1==0:
			netadd=netadd[:netadd.rfind('com/')+4]
	
		#模式一处理完网址都是带‘/’
		#处理斜杠，index目录有些可能开头有斜杠
		if wid2==1:
			netadd=netadd[:-1]
		#print(netadd)
		return netadd


	#此函数用于文件名前补0
	def get_file_numb(self,i):
		fname=str(i)
		while len(fname)<6:
			fname='0'+fname
	
		return fname

	#此函数用于格式化index变为index_b
	def read_index(self,str1,str2,str3,wid1):
		'''#函数简介#用法示例
		#函数简介
			str1=str_index_name			index文件名字
			str2=str_index_b_name		index_b的文件名字
			str3=get_indexdata_netadd	请求网址
			wid1	index网址请求模式选择	1追加	0母网页
			index嵌套解决原理：递归

			index_b文件
				第一行写下载req_add_head网址
				之后：编号#源地址
			#str1=re.sub(r'.+#','',str1)#裁剪'编号#源地址'之后获取目录'

			netadd删尾缀m3u8 用rtxt.rfind('/')获取/位置标号，删除之后的字符即可。
			str1=str1[:str1.rfind('/')+1]
		#用法示例
			list1=read_index('index.txt','index_b.txt','https://xxxx/playlist.m3u8')
			if list1[0]!=0:
				print(list1)
		'''
		list_f_name=[0,]
		if self.down_m3u8(str3,str1)==0:
			return list_f_name
		try:
			#尝试打开文件
			f=open(str1,'r')
			fb=open(str2,'w')
			fm3u8=open(str1+'.m3u8','w')
		except:
			#打开文件失败，此时返回的列表[0]为数字0
			return list_f_name
		fb.write(str3.strip()+'\n')#网址写在index_b第一行
		i=0
		#index_str1=f.readline()
		#index_str2=f.readline()
		strindex=f.readline()
		strindex.strip()
		while strindex!='':
			if strindex.startswith('#')==False:
				#列表从标号为1的单元开始存贮
				i=i+1
				#合成标准格式（文件名#请求标签）
				id_name=self.get_file_numb(i)+'.ts'
				strb=id_name+'#'+strindex
				#将index请求地址，存入列表中
				list_f_name.append(strb)
				#print(strb)	#调试用
				fb.write(strb+'\n')
				fm3u8.write(str1+id_name+'\n')
			elif strindex.startswith('#EXT-X-KEY')==False:
				fm3u8.write(strindex.strip()+'\n')#将带‘#’原路写回去
			else:
				print("需要key")
				str_key=re.sub(r'[.]{1}key',".m3u8",strindex)+'\n'
				str_key=re.sub(r'key',str1+'key',str_key)
				fm3u8.write(str_key)
				strb='key.m3u8'+'#'+strindex[strindex.find('"')+1:strindex.rfind('"')]
				list_f_name.append(strb)
				fb.write(strb+'\n')
			strindex=f.readline()
			strindex=strindex.strip()
		f.close()
		fb.close()
		fm3u8.close()
		#拆解index嵌套（网址整理未完成）
		#index目录的文件个数小于六个，可能是一个选择清晰度的文件
		if i<6 and i>0:
			print("0	"+str(list_f_name[0]))
			for k in range(1,len(list_f_name)):
				#输出清晰度选项
				print(str(k)+"	"+list_f_name[k])
			print("请选择清晰度，输入编号即可")
			i=int(sys.stdin.readline().rstrip())
			if i!=0:
				#选好之后调用自己#将返回的值返回#index网址整理方式
				if re.sub(r'.+#','',list_f_name[1]).startswith('/'):
					str3=self.netadd_cat(str3,wid1,1)
					str3=str3+re.sub(r'.+#','',list_f_name[i])
					return self.read_index(str1,str2,str3,wid1)
				else :
					str3=self.netadd_cat(str3,wid1)
					str3=str3+re.sub(r'.+#','',list_f_name[i])
					return self.read_index(str1,str2,str3,wid1)

		print("理论下载"+str(i)+"个文件")
		#将列表第一位设为网址，表示列表整理成功
		if re.sub(r'.+#','',list_f_name[1]).startswith('/'):
			list_f_name[0]=self.netadd_cat(str3,wid1,1)
			self.save_data(str1,i+1,wid1,1)
		else:
			list_f_name[0]=self.netadd_cat(str3,wid1)
			self.save_data(str1,i+1,wid1)
		return list_f_name


	#线程类
	class down_thread(threading.Thread):
		'''
		#用法示例
			thread1 = down_thread(1, "https://xxxx/out000.ts", 'out000.ts')
			thread1.start()
			thread1.join()
			print(list_f_end_id)
		'''
		def __init__(self,f_id,str_netadd,str_fname):
			threading.Thread.__init__(self)
			self.f_id=f_id
			self.str_netadd=str_netadd
			self.str_fname=str_fname
		def run(self):
			#print(str(self.f_id)+self.str_fname+self.str_netadd+"开始下载")	#调试用
			down_key=1
			while down_key==1:
				try:
					#proxies={'https':'https://'+ipwork}
					#req=requests.get(self.str_netadd,proxies=proxies)
					req=requests.get(self.str_netadd)
					fdown=open(self.str_fname,'wb')
					fdown.write(req.content)
					fdown.close()
					down_key=0
				except:
					#print(str(self.f_id)+self.str_fname+self.str_netadd+"下载/保存失败")
					print(str(self.f_id)+self.str_fname+"#",end="")
			

	#创建单个文件的下载线程并开始线程
	def new_a_thread(self,f_id,str_netadd,str_fname):
		#新建一个下载进程，并开始
		new_thread = self.down_thread(f_id, str_netadd, str_fname)
		new_thread.start()
		#new_thread.join()	#解除此注释可能变成单线程程序，未测试

	#此函数将已完成的id和总目录对比，查找缺失（len(list_f_name)，list_f_end_id）
	def he_dui(self,len_list,list_end_id):
		list_end_id.sort()#将下载完成的文件id按小大排序
		#print(list_f_end_id)		#调试用
		list_bad=[0,]
		bad=0
		i_max=len(list_end_id)
		#生成一串连续的id对比目录
		print(str(i_max))
		for i in range(0,i_max):
			if list_end_id[i]>i+bad:
				while list_end_id[i] != i+bad+1:
					#print(list_f_end_id[i])
					bad=bad+1	#失败文件计数器
					list_bad.append(i+bad)		#失败文件id添加到列表
			else:
				print(list_end_id[i])
		#print(list_bad)				#调试用	#输出缺少的文件的id
		#到i_max停，是防止访问列表未知区域，造成程序终止
		list_bad[0]=bad
		for i in range(list_end_id[-1]+1,len_list-list_bad[0]):
			bad=bad+1
			list_bad.append(i+list_bad[0])			#失败文件id添加到列表
		print("缺少的文件个数为"+str(bad))	#调试用
		'''list_bad介绍
		list_bad[0]存储下载失败的个数
		list_bad[0+]存储下载失败的文件的id
		'''
		list_bad[0]=bad
		return list_bad


	#为每个ts文件创建一个线程去下载。并且查漏
	def while_down(self,f_name_head,list_f_name,req_add_head,g_f_id_min,g_f_id_max):
		'''参数定义
		f_name_head		文件名字的头
		list_f_name		请求目录名字
		req_add_head	请求地址的头网址	要求：req_add_head+list_f_name[n]可以请求ts
		g_f_id_min		从列表建立下载的开始位置	默认从1开始
		g_f_id_max		从列表建立下载的终止位置	默认全部
		'''

		timeout_numb=0	#计数(时)器

		start_thread=threading.activeCount()
		#系统同时存在的初始线程常数
		
		min_thread=start_thread+self.add_thread
		#f_id 记录当前创建的线程位于请求目录的坐标
		f_id=0
		if g_f_id_min<1:
			f_id=1
		else:
			f_id=g_f_id_min

		#f_id_max 储存最后一个线程位于请求目录的坐标
		f_id_max=len(list_f_name)
		if g_f_id_max<=f_id:
			f_id_max=f_id+1
		elif g_f_id_max<f_id_max:
			f_id_max=g_f_id_max

		while f_id<f_id_max:
			#判断当前线程数
			#线程数不足进程常量，开始创建下载线程
			while threading.activeCount()<min_thread and f_id<f_id_max:
				#组合请求地址	#index网址整理方式
				str_netadd=req_add_head+re.sub(r'.+#','',list_f_name[f_id])
				#组合文件名称 文件名0000123.ts
				str_fname=f_name_head+re.sub(r'#.+','',list_f_name[f_id])
				#建立线程
				#print(str(threading.activeCount()))		#调试用#输出当前线程数量
				#print(f_id,str_netadd,str_fname)
				self.new_a_thread(f_id,str_netadd,str_fname)
				f_id=f_id+1
				timeout_numb=0

			if f_id==f_id_max:
				break
			#认为当前有死亡进程
			elif timeout_numb > self.timeout_max:
				#认为当前有死亡进程，将进程常数增加
				print('线程数被增加')
				min_thread=min_thread+self.add_thread
				#判断死亡线程是否过多，为内存条减压
				if min_thread>self.max_thread:
					print('是否继续增加子线程上限')
					print('请输入int（0结束）')
					num = int(sys.stdin.readline().rstrip())
					if num>0:
						self.max_thread=self.max_thread+num
					else:
						if input('线程超出预计，按回车结束程序（所有进程）')=="":
							os._exit(1)
				#重新开始计时
				timeout_numb=0
			else:
				time.sleep(1)
				timeout_numb=timeout_numb+1

		#程序至此，已经不需要再按顺序建立线程
		print("进入延时等待部分线程")
		timeout_numb=0

		#如果有未判定死亡线程仍未完成下载，等待timeout_max

		while timeout_numb<self.timeout_max and threading.activeCount()>(min_thread-self.add_thread):
			time.sleep(1)
			timeout_numb=timeout_numb+1
		if threading.activeCount()>start_thread:
			return 1
		else:
			return 0

	#存档
	def save_data(self,f_name_head,len_list,wid1,wid2=0):
		f_cund=open(f_name_head+"存档.txt","w")
		f_cund.write('len='+str(len_list)+'\n')
		f_cund.write('wid1='+str(wid1)+'\n')
		f_cund.write('wid2='+str(wid2)+'\n')
		f_cund.close()

	#读档	
	def read_data(self,f_name):
		'''#硬读档，直接读取文件夹内容
		f_name		文件名
		返回		list_bad
		'''
		filename=f_name+"filelist.txt"		#临时存档
		os.system('dir|find /i ".ts"|find /i "'+f_name+'">'+filename)
		f=open(filename,'r')
		list_end_id=list()
		str1=f.readline()
		while str1!='':
			try:
				str2=re.sub(r'.+'+f_name,'',str1)
				str2=re.sub(r'\.{1}ts{1}.*','',str2)
				list_end_id.append(int(str2))
			except:
				print("str1")
			str1=f.readline()
		f.close()
		os.system('del '+filename)
		print("读取文件结束")
		#print(list_end_id)
		print("读取"+f_name+"存档")
		f1=open(f_name+'存档.txt','r')
		len_list=int(re.sub(r'.*len=','',f1.readline()))
		f1.close()
		#return he_dui(len(list_f_name),list_end_id)
		return self.he_dui(len_list,list_end_id)

	#下载list_bad
	def down_list_bad(self,list_bad,list_f_name,req_add_head,f_name_head):
		'''
		list_bad
		list_f_name
		req_add_head
		f_name_head
		'''
		timeout_numb=0
		min_thread=threading.activeCount()+20
		print("查漏剩余"+str(list_bad))
		thread_star=threading.activeCount()
		for i in list_bad[1:]:
			#根据id重新建立死亡线程
			#组合请求地址	#index网址整理方式
			str_netadd=req_add_head+re.sub(r'.+#','',list_f_name[i])
			#组合文件名称 文件名0000123.ts
			str_fname=f_name_head+re.sub(r'#.+','',list_f_name[i])
			print(str_netadd,str_fname)
			#print(str(i))	#调试用	
			self.new_a_thread(i,str_netadd,str_fname)
			#防止一下创建线程过多
			timeout_numb=0#计时器清零
			if threading.activeCount()>=min_thread:
				while threading.activeCount()>=min_thread and timeout_numb<40:
					time.sleep(1)
					timeout_numb=timeout_numb+1
				if timeout_numb>=39:
					timeout_numb=0
					min_thread=min_thread+self.add_thread
				else:
					timeout_numb=0

		#补漏线程创建结束，等待线程下载
		while timeout_numb<self.timeout_max and threading.activeCount()>thread_star:
			time.sleep(1)
			timeout_numb=timeout_numb+1


	def read_index_b(self,f_name):
		list_f_name=[0,]
		try:
			fb=open(f_name+"存档.txt",'r')
		except:
			return list_f_name
		fb.readline()
		wid1=int(re.sub(r'.*wid1=','',fb.readline().strip()))
		wid2=int(re.sub(r'.*wid2=','',fb.readline().strip()))
		fb.close()
		f=open(f_name+"_b",'r')
		str1=f.readline().strip()
		list_f_name[0]=self.netadd_cat(str1,wid1,wid2)
		str1=f.readline().strip()
		while str1!="":
			list_f_name.append(str1)
			str1=f.readline().strip()
		f.close()
		return list_f_name


	def key_open(self,str_key_f):
		try:
			f=open(str_key_f,'r')
			str1=f.readline()
			if str1.strip()!="":
				f.close()
				return 1
			else :
				f.close()
				return 0
		except:
			return -1

	#可以下载嵌套index文件，但是需要定位到index文件，选择工作模式
	def main_down(self,url,f_name,wid1):
		'''
		url="https://xxx/index.m3u8"
		f_name="冰菓"
		wid1=0		index网址请求模式选择	1追加	0母网页
		'''
		print(url+f_name)
		list_f_name=self.read_index(f_name,f_name+"_b",url,wid1)
		if list_f_name[0]!=0:
			print(list_f_name[0])
			print("下载中...")
			
			if list_f_name[1].find('key.')>=0:
				str_key=f_name+list_f_name.pop(1)
				while self.key_open(re.sub(r'#.+','',str_key))<=0:
					self.new_a_thread(-1,list_f_name[0]+re.sub(r'.+#','',str_key),re.sub(r'#.*','',str_key))
					#print(list_f_name[0]+re.sub(r'.+#','',str_key)+re.sub(r'#.*','',str_key))
					print('已建立线程'+str_key)
					time.sleep(10)
				print('key已完成，开始下载ts文件')
			self.while_down(f_name,list_f_name,list_f_name[0],0,len(list_f_name))
			time.sleep(10)
			list_bad=self.read_data(f_name)
			while 1:
				if list_bad[0]!=0:
					self.down_list_bad(list_bad,list_f_name,list_f_name[0],f_name)
					time.sleep(5)
					list_bad=self.read_data(f_name)
				else :
					break

			#input("回车开始合并文件")
			self.addf(f_name)
			list_f_name.clear()
			list_bad.clear()
			return 1
		list_f_name.clear()
		list_bad.clear()
		return 0


	#读档模式
	def main_readdata(self,f_name):
		list_f_name=self.read_index_b(f_name)
		str_key=""
		if list_f_name[1].find('key.')>=0:
			str_key=f_name+list_f_name.pop(1)
		#print(list_f_name)
		list_bad=self.read_data(f_name)
		if list_f_name[0]==0:
			print('查无此挡'+f_name)
			return 0
		#先下载key文件，再下载ts文件
		if str_key!="":
			while self.key_open(re.sub(r'#.+','',str_key))<=0:
				self.new_a_thread(-1,list_f_name[0]+re.sub(r'.+#','',str_key),re.sub(r'#.*','',str_key))
				print('已建立线程'+str_key)
				time.sleep(10)
		while list_bad[0]!=0:
			self.down_list_bad(list_bad,list_f_name,list_f_name[0],f_name)
			list_bad=self.read_data(f_name)
			print(list_bad)

		#input("回车开始合并文件")
		self.addf(f_name)
		list_f_name.clear()
		list_bad.clear()
		return 1

'''
	#初次下载模式(index文件请求网址，文件名，ts文件网址组合方式)
	#main_down(url,f_name,wid1)

	#读档查漏模式(文件名)
	#main_readdata(f_name)
'''


