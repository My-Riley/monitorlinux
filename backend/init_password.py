"""生成初始密码哈希值"""

import bcrypt

password = "admin123"
hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
print(f"Password: {password}")
print(f"Hashed: {hashed}")
print("\nSQL UPDATE语句:")
print(f"UPDATE sys_user SET password = '{hashed}' WHERE user_id = 1;")
