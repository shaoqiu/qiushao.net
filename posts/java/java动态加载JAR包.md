java动态加载JAR包
------
**create time: 2015-07-10; update time: 2015-07-10**

---------------------------------------------------------------

### 1. why
在开发过程中有时候会遇到一些需要经常变化的逻辑，甚至一些功能需要增减。按常规的开发模式的话，功能逻辑变化或者功能增减都需要更新整个应用。但有时候更新整个应用，是一件麻烦的事。需要走各种流程，审核。所以我们把部分经常需要变化的功能模块提取出来，作为插件。当这部分逻辑有变化时，只需要更新插件就可以了。我们可以把插件放到服务器上，客户端每次启动都检查一下服务器的插件是否有更新，有更新的话就下载替换本地的插件即可。这样就能很灵活的更新了。

### 2. how
上面讨论了插件化开发的理由，那我们怎么去实现这样的框架呢？我们可以将程序划分为三个部分：`接口`，`宿主程序`，`插件`。接口作为宿主程序和插件通讯的桥梁。宿主程序要能和插件进行通信，必须共同遵守某种协议。这个协议应该由宿主程序来规定。宿主程序应该规定通讯接口，及各种约定：
- 所有插件都必须实现宿主程序提供的接口。
- 插件的命名约定：类的全名_版本号.jar（如"com.shaoqiu.shape.Circle_0.01.jar"），类的全名必须是实现了宿主程序接口的类。
- 插件发布时不能将宿主提供的接口JAR文件一起打包（避免冲突，减少体积）。

好了，有以上的约定就可以开始了。下面我们就来举个小例子来讨论一下。
#### 2.1. 首先由宿主程序提供一个接口
新建一个 JAVA 工程**Shape**，创建以下文件。<br/>
`Shape.java`：
```java
package com.shaoqiu.shape;

public interface Shape {
	public void shapeName();
}
```
这就是宿主程序提供的接口，这个接口是一个形状，有一个方法用来打印自己的形状名称。将这个工程导出为一个`jar`文件，名为`shape.jar`，后面的插件开发都需要导入这个`jar`文件。导出的时候记得不要勾选`.classpath`和`.project`文件
#### 2.2. 实现插件
新建另一个 JAVA 工程作为插件工程，名为**Circle**，导入上面的`shape.jar`，并创建以下文件。<br/>
`Circle.java`：
```java
package com.shaoqiu.shape.circle;
import com.shaoqiu.shape.Shape;

public class Circle implements Shape{
	@Override
	public void shapeName() {
		System.out.println("I am Circle");
	}
}
```
将这个工程导出为`com.shaoqiu.shape.circle.Circle_0.01.jar`，导出的时候记得不要勾选`shape.jar`还有`.classpath`和`.project`文件，这样我们的第一个插件就已经完成了。

#### 2.2. 实现宿主程序
新建另一个 JAVA 工程作为宿主工程，名为**Host**，导入上面的`shape.jar`，创建以下文件。 <br/>
`Main.java`：
```java
package com.shaoqiu.host;

import java.io.File;
import java.net.URL;
import java.net.URLClassLoader;
import com.shaoqiu.shape.Shape;

public class Main {

	public static void main(String[] args) {
		System.out.println("running host...");
		String urlPattern = "file:///";
		String pluginPath = "D:/plugins";

		File plugin = new File(pluginPath);
		File[] jarList = plugin.listFiles();

		ClassLoader cl = null;
		String jarPath = null;
		String className = null;
		try {
			for (File jar : jarList) {
				className = jar.getName().split("_")[0];
				jarPath = urlPattern + pluginPath + "/" + jar.getName();
				cl = new URLClassLoader(new URL[] { new URL(jarPath) });
				Class<?> c = cl.loadClass(className);
				Shape impl = (Shape) c.newInstance();
				impl.shapeName();
			}
		} catch (Exception e) {
			e.printStackTrace();
		}
	}
}
```

我们的插件目录为`String pluginPath = "D:/plugins"`，所以需要在D盘下创建一个`plugins`目录，将前面导出的`com.shaoqiu.shape.circle.Circle_0.01.jar`插件放到这个目录。执行宿主程序就可以看到：
```
running host...
I am Circle
```
宿主程序成功调用了`Circle`插件的方法。