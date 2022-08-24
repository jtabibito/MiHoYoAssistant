# MiHoYoAssistant
米游社小助手

1.COOKIE获取方式:浏览器自带的调试工具选择Network,然后登录网页版米游社,在"ys/"项中找到Cookie拷贝即可
![1661331265389](https://user-images.githubusercontent.com/34726874/186375589-56de5740-cefc-488a-9513-f901ae9bb8e3.png)

2.在Settings.Secrets中配置COOKIE,'#'分割多个账号的cookie

3.然后在Actions中启动workflow，每日4点自动签到

4.可在.github/workflows/main.yml中配置自动签到时间

## Attention
如果fork的项目一段时间后没有活动,需要手动在Actions中选择继续使用Action,否则会被github关闭Action
