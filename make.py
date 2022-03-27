import win32com.client.makepy as makepy
import win32com.client.gencache as gencache

makepy.main()

path = gencache.GetGeneratePath()

print(path)
