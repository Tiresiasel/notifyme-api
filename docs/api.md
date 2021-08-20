## Api说明文档
1. api.add_resource(News, "/api/news")
    - get方法：获取某个keyword的前limit条新闻<br>
      ```
      params:
        - keyword : str
        - limit(opt) : int  
          
      ret:
        - {"code": "200", "status": "OK", "data": news_list}
      ```     
    
2. api.add_resource(UserRegister, "/api/user/register")
    - get方法：返回用户所要注册的邮箱是否存在
      ```
      params：
        - email:str
   
      ret:
        - {"code": 406, "status": "Not Acceptable: user already exists"} # 用户的邮箱已经存在
        - {"code": 200, "status": "OK"} # 用户的邮箱不存在
      ```
    - post方法：创建邮箱
      ```
      params:
        - email:str
        - username:str
        - password_hash:str
      
      ret:
        - {"code": 406, "status": "Not Acceptable: user already exists"} # 用户邮箱已经存在
        - {"code": 201, "status": "Created"} # 创建成功
      ```
     
3. api.add_resource(UserLogin, "/api/user/login")
    - get方法：登录并获取该用户的token
    ```
    params:
      - email:str
      - password_hash:str
   
    ret:
      - {"code": 200, "status": "OK", "data": {"token": self._generate_auth_token(uid)}} # 密码正确
      - return {"code": 401, "status": "Unauthorized"}) # 密码错误
    ```

4. api.add_resource(UserSubscriptionKeyword, "/api/user/subscription/keyword")
   - get方法：返回该用户订阅的keyword
   ```
   login_required:
      - token
   
   ret:
      - {"code": 200, "status": "OK", "data": keywords_list}
   ```
   - post方法：修改用户订阅的keyword
   ```
   login_required:
      - token
   
   params:
      - keywords_list:str # 列表的字符串
      - operation:str # add or delete
   
   ret:
      - {"code": 201, "status": "Created"} # 增加成功
      - {"code": 200, "status": "OK"} # 删除成功
      - {"code": 501, "status": "Not Implemented"} # 输入了错误的operation指令

   ```

5. api.add_resource(UserSubscriptionChannel, "/api/user/subscription/channel")
   - post方法: 修改用户的channel值
   ```
   login_required:
      - token
   
   params:
      - channel
   
   ret:
      - return {"code": 200, "status": "OK"}
   ```
   
6. api.add_resource(UserForgetPassword,"/api/user/forget-password")
   - get方法: 获取当前用户是否存在
   ```
   params:
      - email:str
   
   ret:
      - {"code": 200, "status": "OK"} # 用户存在
      - {"code": 406, "status": "Not Acceptable: user doesn't exists"} #用户不存在
   ```
   
   - post方法:发送验证码给用户的邮箱
   ```
   params:
      - email:str
   
   ret:
      - {"code": 200, "status": "OK"} # 成功发送验证码给用户
      - {"code": 406, "status": "Not Acceptable: user already exists"} # 用户已经存在
   ```

7. api.add_resource(UserForgetPasswordAuth,"/api/user/forget-password/auth")
   - get方法:判断用户输入的验证码是否和redis中的验证码相同
   ```
   params:
      - email:str
      - code:str
     
   ret: 
      - {"code":200,"status":"OK"}
      - {"code":403,"status":"Forbidden"}