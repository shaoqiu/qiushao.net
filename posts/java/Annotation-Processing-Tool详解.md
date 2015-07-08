Annotation Processing Tool 详解
------

关于APT（Annotation Processing Tool 简称）的讲解资料很少，幸运地找到了一篇英文的讲解，觉得挺详细的，就翻译过来。[原文](http://hannesdorfmann.com/annotation-processing/annotationprocessing101/) 顺便添加了一些自己的理解，及扩展。

---------------------------------------------------------------------------------------------------------------
在这篇文章中我将阐述如何实现一个注解处理器。首先我将向你解释什么是注解处理器，你可以使用这个强大的工具来做什么及不能做什么。接下来我们将一步一步来实现一个简单的注解处理器。

### 1. 一些基本概念
在开始之前，我们需要声明一件重要的事情是：我们不是在讨论在**运行时**通过反射机制运行处理的注解，而是在讨论在**编译时**处理的注解。
注解处理器是 javac 自带的一个工具，用来在编译时期扫描处理注解信息。你可以为某些注解注册自己的注解处理器。这里，我假设你已经了解什么是注解及如何自定义注解。如果你还未了解注解的话，可以查看[官方文档](http://docs.oracle.com/javase/tutorial/java/annotations/index.html)。注解处理器在 Java 5 的时候就已经存在了，但直到 Java 6 （发布于2006看十二月）的时候才有可用的API。过了一段时间java的使用者们才意识到注解处理器的强大。所以最近几年它才开始流行。
一个特定注解的处理器以 java 源代码（或者已编译的字节码）作为输入，然后生成一些文件（通常是`.java`文件）作为输出。那意味着什么呢？你可以生成 java 代码！这些 java 代码在生成的`.java`文件中。因此你不能改变已经存在的java类，例如添加一个方法。这些生成的 java 文件跟其他手动编写的 java 源代码一样，将会被 javac 编译。

### 2. AbstractProcessor
让我们来看一下处理器的 API。所有的处理器都继承了`AbstractProcessor`，如下所示：
```java
package com.example;

import java.util.LinkedHashSet;
import java.util.Set;
import javax.annotation.processing.AbstractProcessor;
import javax.annotation.processing.ProcessingEnvironment;
import javax.annotation.processing.RoundEnvironment;
import javax.annotation.processing.SupportedAnnotationTypes;
import javax.annotation.processing.SupportedSourceVersion;
import javax.lang.model.SourceVersion;
import javax.lang.model.element.TypeElement;

public class MyProcessor extends AbstractProcessor {

	@Override
	public boolean process(Set<? extends TypeElement> annoations,
			RoundEnvironment env) {
		return false;
	}

	@Override
	public Set<String> getSupportedAnnotationTypes() {
		Set<String> annotataions = new LinkedHashSet<String>();
	    annotataions.add("com.example.MyAnnotation");
	    return annotataions;
	}

	@Override
	public SourceVersion getSupportedSourceVersion() {
		return SourceVersion.latestSupported();
	}

	@Override
	public synchronized void init(ProcessingEnvironment processingEnv) {
		super.init(processingEnv);
	}

}
```

- `init(ProcessingEnvironment processingEnv)` ：所有的注解处理器类**都必须有一个无参构造函数**。然而，有一个特殊的方法`init()`，它会被注解处理工具调用，以`ProcessingEnvironment`作为参数。ProcessingEnvironment 提供了一些实用的工具类`Elements`, `Types`和`Filer`。我们在后面将会使用到它们。

- `process(Set<? extends TypeElement> annoations, RoundEnvironment env)` ：这类似于每个处理器的`main()`方法。你可以在这个方法里面编码实现扫描，处理注解，生成 java 文件。使用`RoundEnvironment` 参数，你可以查询被特定注解标注的元素（原文：you can query for elements annotated with a certain annotation ）。后面我们将会看到详细内容。

- `getSupportedAnnotationTypes()`：在这个方法里面你必须指定哪些注解应该被注解处理器注册。注意，它的返回值是一个`String`集合，包含了你的注解处理器想要处理的注解类型的全称。换句话说，你在这里定义你的注解处理器要处理哪些注解。

- `getSupportedSourceVersion()` ： 用来指定你使用的 java 版本。通常你应该返回`SourceVersion.latestSupported()` 。不过，如果你有足够的理由坚持用 java 6 的话，你也可以返回`SourceVersion.RELEASE_6`。我建议使用`SourceVersion.latestSupported()`。在 Java 7 中，你也可以使用注解的方式来替代重写`getSupportedAnnotationTypes()` 和 `getSupportedSourceVersion()`，如下所示：
```java
@SupportedSourceVersion(value=SourceVersion.RELEASE_7)
@SupportedAnnotationTypes({
   // Set of full qullified annotation type names
	"com.example.MyAnnotation",
	"com.example.AnotherAnnotation"
 })
public class MyProcessor extends AbstractProcessor {

	@Override
	public boolean process(Set<? extends TypeElement> annoations,
			RoundEnvironment env) {
		return false;
	}
	@Override
	public synchronized void init(ProcessingEnvironment processingEnv) {
		super.init(processingEnv);
	}
}
```
由于兼容性问题，特别是对于 android ，我建议重写`getSupportedAnnotationTypes()` 和 `getSupportedSourceVersion()` ，而不是使用 `@SupportedAnnotationTypes` 和 `@SupportedSourceVersion`。

接下来你必须知道的事情是：注解处理器运行在它自己的 JVM 中。是的，你没看错。javac 启动了一个完整的 java 虚拟机来运行注解处理器。这意味着什么？你可以使用任何你在普通 java 程序中使用的东西。使用 `guava`! 你可以使用依赖注入工具，比如`dagger`或者任何其他你想使用的类库。但不要忘记，即使只是一个小小的处理器，你也应该注意使用高效的算法及设计模式，就像你在开发其他 java 程序中所做的一样。

### 3. 注册你的处理器
你可能会问 “怎样注册我的注解处理器到 javac ？”。你必须提供一个`.jar`文件。就像其他 .jar 文件一样，你将你已经编译好的注解处理器打包到此文件中。并且，在你的 .jar 文件中，你必须打包一个特殊的文件`javax.annotation.processing.Processor`到`META-INF/services`目录下。因此你的 .jar 文件目录结构看起来就你这样：
```
MyProcess.jar
	-com
		-example
			-MyProcess.class
	-META-INF
		-services
			-javax.annotation.processing.Processor
```
`javax.annotation.processing.Processor` 文件的内容是一个列表，每一行是一个注解处理器的全称。例如：
```
com.example.MyProcess
com.example.AnotherProcess
```

### 4. 例子：工厂模式
现在可以举一个实际的例子了。我们使用`Eclipse`作为开发环境（原文使用的是 maven，但我对 maven 不熟悉，也没有 maven 环境，所以将开发环境改成了 Eclipse）。最后我将会把例子的代码放到 `github`上。
首先，我必须要说的是，想要找到一个可以使用注解处理器去解决的简单问题来当作教程，并不是一件容易的事。这篇教程中，我们将实现一个非常简单的工厂模式（不是抽象工厂模式）。它只是为了给你简明的介绍注解处理器的API而已。所以这个问题的程序，并不是那么有用，也不是一个真实开发中的例子。再次声明，你能学到的只是注解处理器的相关内容，而不是设计模式。

我们要解决的问题是：我们要实现一个 pizza 店，这个 pizza 店提供给顾客两种 pizza （Margherita 和 Calzone），还有甜点 Tiramisu（提拉米苏）。
简单看一下这段代码：
`Meal.java`：
```java
package com.example.pizza;

public interface Meal {
	public float getPrice();
}
```

`MargheritaPizza.java`：
```java
package com.example.pizza;

public class MargheritaPizza implements Meal{
	@Override
	public float getPrice() {
		return 6.0f;
	}
}
```

`CalzonePizza.java`：
```java
package com.example.pizza;

public class CalzonePizza implements Meal{
	@Override
	public float getPrice() {
		return 8.5f;
	}
}
```

`Tiramisu.java`：
```java
package com.example.pizza;

public class Tiramisu implements Meal{
	@Override
	public float getPrice() {
		return 4.5f;
	}
}
```

顾客要在我们的 pizza 店购买食物的话，就得输入食物的名称：
`PizzaStore.java`：
```java
package com.example.pizza;

import java.util.Scanner;

public class PizzaStore {

	public Meal order(String mealName) {
		if (null == mealName) {
			throw new IllegalArgumentException("name of meal is null!");
		}
		if ("Margherita".equals(mealName)) {
			return new MargheritaPizza();
		}

		if ("Calzone".equals(mealName)) {
			return new CalzonePizza();
		}

		if ("Tiramisu".equals(mealName)) {
			return new Tiramisu();
		}

		throw new IllegalArgumentException("Unknown meal '" + mealName + "'");
	}

	private static String readConsole() {
		Scanner scanner = new Scanner(System.in);
		String meal = scanner.nextLine();
		scanner.close();
		return meal;
	}
	
	public static void main(String[] args) {
		System.out.println("welcome to pizza store");
		PizzaStore pizzaStore = new PizzaStore();
		Meal meal = pizzaStore.order(readConsole());
		System.out.println("Bill:$" + meal.getPrice());
	}
}
```

正如你所见，在`order()`方法中，我们有许多 if 条件判断语句。并且，如果我们添加一种新的 pizza 的话，我们就得添加一个新的 if 条件判断。但是等一下，使用注解处理器和工厂模式，我们可以让一个注解处理器生成这些 if 语句。如此一来，我们想要的代码就像这样子：
`PizzaStore.java`：
```java
package com.example.pizza;

import java.util.Scanner;

public class PizzaStore {

	private MealFactory factory = new MealFactory();
	
	public Meal order(String mealName) {
		return factory.create(mealName);
	}

	private static String readConsole() {
		Scanner scanner = new Scanner(System.in);
		String meal = scanner.nextLine();
		scanner.close();
		return meal;
	}
	
	public static void main(String[] args) {
		System.out.println("welcome to pizza store");
		PizzaStore pizzaStore = new PizzaStore();
		Meal meal = pizzaStore.order(readConsole());
		System.out.println("Bill:$" + meal.getPrice());
	}
}
```

`MealFactory` 类应该是这样的：
`MealFactory.java`：
```java
package com.example.pizza;

public class MealFactory {

	public Meal create(String id) {
		if (id == null) {
			throw new IllegalArgumentException("id is null!");
		}
		if ("Calzone".equals(id)) {
			return new CalzonePizza();
		}

		if ("Tiramisu".equals(id)) {
			return new Tiramisu();
		}

		if ("Margherita".equals(id)) {
			return new MargheritaPizza();
		}

		throw new IllegalArgumentException("Unknown id = " + id);
	}
}
```

### 5. @Factory Annotation
能猜到么，我们打算使用注解处理器生成`MealFactory`类。更一般的说，我们想要提供一个注解和一个处理器用来生成工厂类。
让我们看一下`@Factory`注解：
`Factory.java`：
```java
package com.example.apt;

import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;

@Target(ElementType.TYPE)
@Retention(RetentionPolicy.CLASS)
public @interface Factory {

	/**
	 * The name of the factory
	 */
	Class<?> type();

	/**
	 * The identifier for determining which item should be instantiated
	 */
	String id();
}
```

思想是这样的：我们注解那些食物类，使用`type()`表示这个类属于哪个工厂，使用`id()`表示这个类的具体类型。让我们将`@Factory`注解应用到这些类上吧：
`MargheritaPizza.java`：
```java
package com.example.pizza;

import com.example.apt.Factory;

@Factory(type=MargheritaPizza.class, id="Margherita")
public class MargheritaPizza implements Meal{

	@Override
	public float getPrice() {
		return 6.0f;
	}
}
```

`CalzonePizza.java`：
```java
package com.example.pizza;

import com.example.apt.Factory;

@Factory(type=CalzonePizza.class, id="Calzone")
public class CalzonePizza implements Meal{

	@Override
	public float getPrice() {
		return 8.5f;
	}
}
```


`Tiramisu.java`：
```java
package com.example.pizza;

import com.example.apt.Factory;

@Factory(type=Tiramisu.class, id="Tiramisu")
public class Tiramisu implements Meal{

	@Override
	public float getPrice() {
		return 4.5f;
	}
}
```

你可能会问，我们是不是可以只将`@Factory`注解应用到`Meal`接口上？答案是不行，因为注解是不能被继承的。即在`class X`上有注解，`class Y extends X`，那么`class Y`是不会继承`class X`上的注解的。在我们编写处理器之前，需要明确几点规则：
1. 只有类能够被`@Factory`注解，因为接口和虚类是不能通过`new`操作符实例化的。
2. 被`@Factory`注解的类必须提供一个默认的无参构造函数。否则，我们不能实例化一个对象。
3. 被`@Factory`注解的类必须直接继承或者间接继承`type`指定的类型。（或者实现它，如果`type`指定的是一个接口）
4. 被`@Factory`注解的类中，具有相同的`type`类型的话，这些类就会被组织起来生成一个工厂类。工厂类以`Factory`作为后缀，例如：`type=Meal.class`将会生成`MealFactory`类。
5. `id`的值只能是字符串，且在它的`type`组中必须是唯一的。

### 6. 注解处理器
我将会通过添加一段代码接着解释这段代码的方法，一步一步引导你。三个点号（`...`）表示省略那部分前面已经讨论过或者将在后面讨论的代码。目的就是为了让代码片段更具有可读性。前面已经说过，我们的完整代码将放到`github`上。OK，让我们开始编写我们的`FactoryProcessor`的框架吧：
`FactoryProcessor.java`：
```java
package com.example.apt;

import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.Map;
import java.util.Set;
import javax.annotation.processing.AbstractProcessor;
import javax.annotation.processing.Filer;
import javax.annotation.processing.Messager;
import javax.annotation.processing.ProcessingEnvironment;
import javax.annotation.processing.RoundEnvironment;
import javax.lang.model.SourceVersion;
import javax.lang.model.element.TypeElement;
import javax.lang.model.util.Elements;
import javax.lang.model.util.Types;

public class FactoryProcessor extends AbstractProcessor {

	private Types typeUtils;
	private Elements elementUtils;
	private Filer filer;
	private Messager messager;
	private Map<String, FactoryGroupedClasses> factoryClasses = 
			new LinkedHashMap<String, FactoryGroupedClasses>();

	@Override
	public synchronized void init(ProcessingEnvironment processingEnv) {
		super.init(processingEnv);
		typeUtils = processingEnv.getTypeUtils();
	    elementUtils = processingEnv.getElementUtils();
	    filer = processingEnv.getFiler();
	    messager = processingEnv.getMessager();
	}

	@Override
	public boolean process(Set<? extends TypeElement> arg0,
			RoundEnvironment arg1) {
		...
		return false;
	}

	@Override
	public Set<String> getSupportedAnnotationTypes() {
		Set<String> annotataions = new LinkedHashSet<String>();
	    annotataions.add(Factory.class.getCanonicalName());
	    return annotataions;
	}

	@Override
	public SourceVersion getSupportedSourceVersion() {
		return SourceVersion.latestSupported();
	}
}
```

在`getSupportedAnnotationTypes()`方法中，我们指定`@Factory`注解将被这个处理器处理。

### 7. Elements and TypeMirrors
在`init()`方法中，我们使用了以下类型：
- Elements：一个用来处理`Element`的工具类（后面详细说明）
- Types：一个用来处理`TypeMirror`的工具类（后面详细说明）
- Filer：正如这个类的名字所示，你可以使用这个类来创建文件

在注解处理器中，我们扫描 java 源文件，源代码中的每一部分都是`Element`的一个特定类型。换句话说：`Element`代表程序中的元素，比如说 包，类，方法。每一个元素代表一个静态的，语言级别的结构。在下面的例子中，我将添加注释来说明这个问题：
```java
package com.example;

public class Foo { // TypeElement

	private int a; // VariableElement
	private Foo other; // VariableElement

	public Foo() {} // ExecuteableElement

	public void setA( // ExecuteableElement
			int newA // TypeElement
	) {
	}
}
```
你得换个角度来看源代码。它只是结构化的文本而已。它不是可以执行的。你可以把它当作 你试图去解析的XML 文件。或者一棵编译中创建的抽象语法树。就像在 XML 解析器中，有许多DOM元素。你可以通过一个元素找到它的父元素或者子元素。
例如：如果你有一个代表`public class Foo`的`TypeElement`，你就可以迭代访问它的子结点：
```java
TypeElement fooClass = ... ;
for (Element e : fooClass.getEnclosedElements()){ // iterate over children
	Element parent = e.getEnclosingElement();  // parent == fooClass
}
```
如你所见，`Elements`代表源代码，`TypeElement`代表源代码中的元素类型，例如类。然后，`TypeElement`并不包含类的相关信息。你可以从`TypeElement`获取类的名称，但你不能获取类的信息，比如说父类。这些信息可以通过`TypeMirror`获取。你可以通过调用`element.asType()`来获取一个`Element`的`TypeMirror`。

### 8. Searching For @Factory
让我们一步一步来实现`process()`方法吧。首先我们扫描所有被`@Factory`注解的类：
```java
@Override
public boolean process(Set<? extends TypeElement> annotations, RoundEnvironment roundEnv) {
	for (Element annotatedElement : roundEnv.getElementsAnnotatedWith(Factory.class)) {
		...
	}
	return false;
}
```
这里并没有什么高深的技术。`roundEnv.getElementsAnnotatedWith(Factory.class)` 返回一个被`@Factory`注解的元素列表。你可能注意到我避免说“返回一个被`@Factory`注解的类列表”。因为它的确是返回了一个`Element`列表。记住：`Element`可以是类，方法，变量等。所以，我们下一步需要做的是检查这个元素是否是一个类：
```java
@Override
public boolean process(Set<? extends TypeElement> annotations, RoundEnvironment roundEnv) {
	for (Element annotatedElement : roundEnv.getElementsAnnotatedWith(Factory.class)) {
		if(annotatedElement.getKind() != ElementKind.CLASS) {
			...		
			}
	}
	return false;
}
```
为什么需要这样做呢？因为我们要确保只有**class**类型的元素被我们的处理器处理。前面我们已经学过，类是一种`TypeElement`元素。那我们为什么不使用`if (! (annotatedElement instanceof TypeElement))`  来检查呢？这是错误的判断，因为接口也是一种`TypeElement`类型。所以在注解处理器中，你应该避免使用`instanceof`，应该用`ElementKind`或者配合`TypeMirror`使用`TypeKind`。

### 9. 错误处理
在`init()`方法中，我们也获取了一个`Messager`的引用。`Messager`为注解处理器提供了一种报告错误消息，警告信息和其他消息的方式。它不是注解处理器开发者的日志工具。`Messager`是用来给那些使用了你的注解处理器的第三方开发者显示信息的。在[官方文档](http://docs.oracle.com/javase/7/docs/api/javax/tools/Diagnostic.Kind.html)中描述了不同级别的信息。非常重要的是`Kind.ERROR`，因为这种消息类型是用来表明我们的注解处理器在处理过程中出错了。有可能是第三方开发者误使用了我们的`@Factory`注解（比如，使用`@Factory`注解了一个接口）。这个概念与传统的 java 应用程序有一点区别。传统的 java 应用程序出现了错误，你可以抛出一个异常。如果你在`process()`中抛出了一个异常，那 jvm 就会崩溃。注解处理器的使用者将会得到一个从 javac 给出的非常难懂的异常错误信息。因为它包含了注解处理器的堆栈信息。因此注解处理器提供了`Messager`类。它能打印漂亮的错误信息，而且你可以链接到引起这个错误的元素上。在现代的IDE中，第三方开发者可以点击错误信息，IDE会跳转到产生错误的代码行中，以便快速定位错误。
回到`process()`方法的实现。如果用户将`@Factory`注解到了一个非`class`的元素上，我们就抛出一个错误信息：
```java
	@Override
	public boolean process(Set<? extends TypeElement> annotations,
			RoundEnvironment roundEnv) {
		for (Element annotatedElement : roundEnv.getElementsAnnotatedWith(Factory.class)) {
			if(annotatedElement.getKind() != ElementKind.CLASS) {
				error(annotatedElement, "Only classes can be annotated with @%s",
			            Factory.class.getSimpleName());
				return true; // Exit processing
			}
	    }
		return false;
	}

	private void error(Element e, String msg, Object... args) {
	    messager.printMessage(
	    	Diagnostic.Kind.ERROR,
	    	String.format(msg, args),
	    	e);
	  }
```
为了能够获取`Messager`显示的信息，非常重要的是注解处理器必须不崩溃地完成运行。这就是我们在调用`error()`后执行`return true`的原因。如果我们在这里没有返回的话，`process()`就会继续运行，因为`messager.printMessage( Diagnostic.Kind.ERROR)`并不会终止进程。如果我们没有在打印完错误信息后返回的话，我们就可能会运行到一个空指针异常等等。就像前面所说的，如果我们继续运行`process()`，一旦有处理的异常在`process()`中被抛出，javac 就会打印注解处理器的空指针异常堆栈信息，而不是`Messager`显示的信息。

### 10. 数据模型