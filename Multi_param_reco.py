
# coding: utf-8

# In[1]:

import sys
from numpy import *
import mysql.connector

#uid = int(sys.argv[1])
#tid = str(sys.argv[2])
uid = 14
tid = str(1)
curr_user_index_ratings = 0
curr_user_index_params = 0
num_videos=0
num_users=0

cnx = mysql.connector.connect(user='root', password='',host='127.0.0.1', database='soc')
#cursors :)====================
cursor_num_users = cnx.cursor()
cursor_num_videos = cnx.cursor()
cursor_ratings = cnx.cursor()
cursor_params_matrix = cnx.cursor()
cursor_user_params = cnx.cursor()
#=================================

query_num_users = ("select ID from users")

cursor_num_users.execute(query_num_users) 

for(UID) in cursor_num_users:
    #print(ID,Username)
    num_users = num_users+1

#total number of users

cursor_num_users.close() 

query_num_videos = ("select VID from videos")
cursor_num_videos.execute(query_num_videos) 

for(VID) in cursor_num_videos:
    #print(VID,Name)
    num_videos = num_videos+1

#total number of videos

cursor_num_videos.close()

#initialize attributes
num_params=6
#[difficulty,relevance,complexity,length,production,engaging]


# In[4]:


#create ratings matrix from database
#old ratings matrix 
#=================================================================
#ratings = random.randint(6, size = (num_videos, num_users), dtype=int)
#ratings
#commenting it out!
#=================================================================
#new ratings
#=================================================================
#take ratings from ratings table in the db!

query_ratings = ("select * from ratings")
cursor_ratings.execute(query_ratings)
ratings = [[0 for i in range(num_videos)] for j in range(num_users)]

#ratings matrix is like:
#       video1 video2 video3 .........................
#user1     0     0      0
#user2     0     0      0
#user3     0     0      0
#.
#.
#.
#it will be fetched by ratings[user][video]

result = cursor_ratings.fetchall()
for row in result:
    for i in range(num_users):
        if(row[0]==uid):curr_user_index_ratings = i
        #assigning index of current user which is in ratings matrix.
        #i.e. the position of row in which ratings of current user is present
        for j in range(num_videos):
            ratings[i][j] = row[j+1]
ratings
cursor_ratings.close()
#ratings table updated 
#=================================================================
# In[5]:


#create params_matrix 
#old params_matrix, I will comment this out!
#=================================================================
params_matrix = random.random(size=(num_videos,num_params))
params_matrix
#=================================================================
#new params_matrix after taking values from db!
#=================================================================
query_params_matrix = ("select difficulty,relevance,complexity,length,production,engaging from videos")
cursor_params_matrix.execute(query_params_matrix)
result_params_matrix = cursor_params_matrix.fetchall()

params_matrix = [[0 for x in range(num_params)] for y in range(num_videos)]
for row in result_params_matrix:
    for i in range(num_videos):
        for j in range(num_params):
            params_matrix[i][j] = row[j]
params_matrix
cursor_params_matrix.close()
#params_matrix updated with values from db!
#=================================================================

# In[7]:


#convert params_matrix to unit vectors
for video in range(num_videos):
    norm=linalg.norm(params_matrix[video,:])
    params_matrix[video][:] = [x / norm for x in params_matrix[video]]
params_matrix


# In[8]:


#load user params
#old user_params, I will comment this out!
#=================================================================
#user_params = random.random(size=(num_users,num_params))
#user_params
#=================================================================
#new user_params after taking values from db!
#=================================================================
user_params = [[0 for x in range(num_params)] for y in range(num_users)]
query_user_params = ("select ID,difficulty,relevance,complexity,length,production,engaging from users")
cursor_user_params.execute(query_user_params)
result_user_params = cursor_user_params.fetchall()
for row in result_user_params:
    for i in range(num_users):
        if(row[0]==uid):curr_user_index_params = i
        #assigning curr_user_index_params to be used to find cost!
        for j in range(num_params):
            user_params[i][j] = row[j+1]
user_params
cursor_user_params.close()
#updated user_params from table users!
#=================================================================

#convert user_params to unit vectors

for user in range(num_users):
    norm=linalg.norm(user_params[user])
    user_params[user][:] = [x / norm for x in user_params[user]]
user_params


# In[10]:


#rated matrix tells whether a particular movie is rated or not
rated_matrix=(ratings!=0)
rated_matrix
#same structure as ratings matrix!

# In[11]:


#get current user index and current topic
#create an array of video indexes video_index[] of all videos belonging 
#to current topic
#such that ratings[user_index][video_index[i]]=0 implies nhy7
#USER is new to the topic

#curr_user_index = already assigned

#we can fetch the index of array row which consists of this 
#uid and the use it in line 177 because it is not neccesary that curr_user_index
#will always be equal to that index, it can be discontinuous!

#curr_topic is replaced by "tid" which we are getting from php file!

video_index = []
for i in range(num_videos):
    if rated_matrix[curr_user_index_ratings][i]==False:
        video_index.append(i)
video_index

if(size(video_index)==0):print("No videos to recommend!")
#nothing to recommend, user have already seen all of then :)    


# In[12]:


#get topic_cost of each video, with respect to curr_topic
#closer two topics are, lower the topic_cost
#create an appropriate function to calculate topic_cost with current_topic
#as argument

# '''topic_cost=random.randint(3,size=(num_videos,),dtype=int)
# topic_cost=topic_cost+ones((size(topic_cost),))
# topic_cost'''


# In[13]:


#get var for each user other than current_user
#var=error*topic_cost summed over each video
#var represents rmse*topic_cost. high var => less effect on prediction
# we can neglect those videos which current_user has not watched
def calc_user_var(curr_user,user_params):
    var_mat = zeros(num_users)
    for user in range(num_users):
        if user == curr_user:
            continue
        else:
            for x in range(num_params):
                var_mat[user] += (user_params[user][x] - user_params[curr_user][x])**2
            
    return var_mat
            


    
# In[14]:


user_var = calc_user_var(curr_user_index_params,user_params)
user_var


# In[15]:


#higher the var, lower the value of that user's prediction
user_val = [1 - x for x in user_var]
user_val


# In[16]:


video_rated = zeros(size(video_index))
p=0
for video in video_index:
    count=0
    for user in range(num_users):
        if user == curr_user_index_ratings:
            continue
        else:
            video_rated[p] += ratings[user][video]*user_val[user]
            if rated_matrix[user][video] == True:
                count+=1
    video_rated[p] /= count
    p+=1

video_rated

#close the db connection!
cnx.close()  
