java类的加载机制
------
**create time: 2015-07-15; update time: 2015-07-15**

---------------------------------------------------------------
### 1. class 的生命周期
就像 android 世界中的 activity 有一个生命周期一样，在 java 世界中的 class 也有它们的生命周期。一个 class 的完整生命周期是这样的：
**Loading（加载）** --> **Verification（验证）** --> **Preparation（准备）** --> **Resolution（解析）** --> **Initilization（初始化）** --> **Using（使用）** --> **Unloading（卸载）**

在加载阶段，虚拟机需要完成以下三件事：
1. 通过一个类的全限定名(fully qualified name)来获取定义此类的二进制字节流。
2. 将这个字节流所代表的静态存储结构转化为方法区的运行时数据结构。
3. 在内存中生成一个代表这个类的`java.land.Class`对象，作为方法区这个类的各种数据的访问入口。

这些规定都是比较灵活的，比如说第一点，只规定了根据全限定名来获取字节流，但是并没有指明要从哪里获取，怎样获取。这也就给了我们发挥想象力的空间。这个字节流我们可以从`.class`文件中读取，可以从数据库中获取，可以从网络下载，甚至可以在运行时动态生成。java虚拟机的实现方式给我们的想象力提供了这个可能。

类的加载阶段是通过类加载器来完成的。相对于类加载的其他阶段而言，加载阶段（准确地说，是加载阶段获取类的二进制字节流的动作）是可控性最强的阶段，因为开发人员既可以使用系统提供的类加载器来完成加载，也可以自定义自己的类加载器来完成加载。下面我们就来讨论一下类加载器。

### 2. 内置类加载器
站在Java虚拟机的角度来讲，只存在两种不同的类加载器：
- （Bootstrap ClassLoader）启动类加载器：它使用C++实现的，是虚拟机自身的一部分。
- 其他所有的类加载器：这些类加载器都是由 java 语言实现的，独立于虚拟机之外，并且全部都直接或间接继承了抽象类`java.land.ClassLoader`。

从 java 开发人员的角度看，类加载器还可以划分得更细致一些：
- （Bootstrap ClassLoader）启动类加载器：这个类加载器负责将存放在`<JAVA_HOME/lib`目录，或使用`-Xbootclasspath`参数指定的路径下的类库加载到虚拟机内存中。启动类加载器无法被 java 程序直接引用。
- 扩展类加载器（Extension ClassLoader）：这个加载器由`sun.misc.Launcher$ExtClassLoader`实现，负责加载`<JAVA_HOME/lib/ext`目录中的类库，或者被系统变量`java.ext.dirs`所指定的路径中的类库，开发都可以直接使用该类加载器。
- 应用程序类加载器（Application ClassLoader）：这个类加载器由`sun.misc.Launcher$AppClassLoader`实现。由于这个类加载器是`ClassLoader.getSystemClassLoader()`方法的返回值，所以也称它为系统类加载器。负责加载环境变量`CLASS_PATH`指定的类库。开发者可以直接使用该类加载器。

以上就是系统的几个类加载器，当然我们也可以自定义类加载器，用于加载不在上面几个加载器加载路径中的类库。

需要强调的是：对于任意一个类，都需要由加载它的类加载器和这个类本身一同确立其中虚拟中的唯一性。每一个类加载器，都有一个独立的类命名空间。换句话说，就是比较两个类是否相等，只有在这两个类都是由同一个类加载器加载的前提下才是有意义的。否则，即使这两个类来源于同一个 class 文件，被同一个虚拟机加载，只要加载它们的类加载器不同，那这两个类就必定不相等，例如：
```java
import java.io.InputStream;

class  MyClassLoader extends ClassLoader {

	@Override
	public Class<?> loadClass(String name) throws ClassNotFoundException {
		String fileName = name + ".class";
		try {
			InputStream is = getClass().getResourceAsStream(fileName);
			if(null == is) {
				return super.loadClass(name);
			}
			byte[] b = new byte[is.available()];
			is.read(b);
			return defineClass(name, b, 0, b.length);
		} catch (Exception e) {
			throw new ClassNotFoundException();
		}
	}
}

public class Main {

	/**
	 * @param args
	 * @throws ClassNotFoundException 
	 * @throws IllegalAccessException 
	 * @throws InstantiationException 
	 */
	public static void main(String[] args) throws ClassNotFoundException, InstantiationException, IllegalAccessException {
		MyClassLoader loader1 = new MyClassLoader();
		MyClassLoader loader2 = new MyClassLoader();
		
		Class<?> claz1 = loader1.loadClass("Foobar");
		Class<?> claz2 = loader2.loadClass("Foobar");
		
		Object object1 = claz1.newInstance();
		Object object2 = claz2.newInstance();
		System.out.println("object1:" + object1);
		System.out.println("object2:" + object2);
		System.out.println(object1.getClass() == object2.getClass());
		
		object2 = claz1.newInstance();
		System.out.println("object1:" + object1);
		System.out.println("object2:" + object2);
		System.out.println(object1.getClass() == object2.getClass());
	}
}
```
结果是：
```
object1:Foobar@71591b4d
object2:Foobar@110f965e
false
object1:Foobar@71591b4d
object2:Foobar@1658fe12
true
```

从结果可以确认不同加载器加载同一个 class 文件，所得到的类也是不一样的。
那么问题来了，假如我写了一个`java.land.Object`类，并且将它放到`CLASS_PATH`目录下，那么系统会不会产生两个不同的`Object`类呢？一个由启动类加载器加载，另一个由系统类加载器加载。当然不会，因为如果这样的话，那 java 类型体系中最基础的行为就没法保证，系统就会乱套了。那怎样才能避免这种情况发生呢？答案是**Parents Delegation Model（双亲委派模型）**。

### 3. 双亲委派模型
这是Java设计者们推荐给开发者的一种类的加载器实现方式。这种模型可以用下图来表示：<br/>
![双亲委派模型](http://img.blog.csdn.net/20140105211242593)
<br/>
我们把每一层上面的类加载器叫做当前层类加载器的父加载器，当然，它们之间的父子关系并不是通过继承关系来实现的，而是使用组合关系来复用父加载器中的代码。该模型在JDK1.2期间被引入并广泛应用于之后几乎所有的Java程序中，但它并不是一个强制性的约束模型，而是Java设计者们推荐给开发者的一种类的加载器实现方式。
该模型的工作流程是：如果一个类加载器收到了类加载的请求，它首先不会自己去尝试加载这个类，而是把请求委托给父加载器去完成，依次向上，因此，所有的类加载请求最终都应该被传递到顶层的启动类加载器中，只有当父加载器在它的搜索范围中没有找到所需的类时，即无法完成该加载，子加载器才会尝试自己去加载该类。
双亲模式的实现方式如下：<br/>
`ClassLoader.java`：
```java
protected Class<?> loadClass(String name, boolean resolve)
        throws ClassNotFoundException
    {
        synchronized (getClassLoadingLock(name)) {
            // First, check if the class has already been loaded
            Class c = findLoadedClass(name);
            if (c == null) {
                long t0 = System.nanoTime();
                try {
                    if (parent != null) {
                        c = parent.loadClass(name, false);
                    } else {
                        c = findBootstrapClassOrNull(name);
                    }
                } catch (ClassNotFoundException e) {
                    // ClassNotFoundException thrown if class not found
                    // from the non-null parent class loader
                }

                if (c == null) {
                    // If still not found, then invoke findClass in order
                    // to find the class.
                    long t1 = System.nanoTime();
                    c = findClass(name);

                    // this is the defining class loader; record the stats
                    sun.misc.PerfCounter.getParentDelegationTime().addTime(t1 - t0);
                    sun.misc.PerfCounter.getFindClassTime().addElapsedTimeFrom(t1);
                    sun.misc.PerfCounter.getFindClasses().increment();
                }
            }
            if (resolve) {
                resolveClass(c);
            }
            return c;
        }
    }
```

其逻辑很简单，首先判断要加载的类是否已经加载过了，未加载过的话，则调用:
```java
if (parent != null) {
	//
	c = parent.loadClass(name, false);
} else {
	c = findBootstrapClassOrNull(name);
}
```