android 在代码中设置字体大小
------
**create time: 2015-09-14; update time: 2015-09-14**

---------------------------------------------------------------

在android开发中，控件的字体大小一般都是在布局文件XML中设置的，但有时候我们需要动态创建控件或者动态改变控件的字体大小，这时就需要在代码中修改字体的大小了。
设置字体的方法为：
```
TextView.setTextSize(float size);
TextView.setTextSize(int unit, float size);
```

第一个方法不指定字体单位，默认单位为 SP，TextView中的源码如下：
```
public void setTextSize(float size) {
    setTextSize(TypedValue.COMPLEX_UNIT_SP, size);
}
```

有一点坑人的地方是：TextView.setTextSize()的返回值是以像素为单位的，但TextView.setTextSize(float size)却是以SP为单位的。一开始没有仔细看API，被坑了。

字体单位可以指定为：
```
    /** {@link #TYPE_DIMENSION} complex unit: Value is raw pixels. */
    public static final int COMPLEX_UNIT_PX = 0;
    /** {@link #TYPE_DIMENSION} complex unit: Value is Device Independent
     *  Pixels. */
    public static final int COMPLEX_UNIT_DIP = 1;
    /** {@link #TYPE_DIMENSION} complex unit: Value is a scaled pixel. */
    public static final int COMPLEX_UNIT_SP = 2;
    /** {@link #TYPE_DIMENSION} complex unit: Value is in points. */
    public static final int COMPLEX_UNIT_PT = 3;
    /** {@link #TYPE_DIMENSION} complex unit: Value is in inches. */
    public static final int COMPLEX_UNIT_IN = 4;
    /** {@link #TYPE_DIMENSION} complex unit: Value is in millimeters. */
    public static final int COMPLEX_UNIT_MM = 5;
```

一般情况下，我们是把字体的大小配置在dimen.xml中的，我们可以通过以下方法来获取dimen.xml中的配置项：
```
Resources.getDimension(int id);
Resources.getDimensionPixelSize(int id);
Resources.getDimensionPixelOffset(int id);
```

这几种方法看起来很相似，它们有什么区别呢？
- getDimension：根据当前DisplayMetrics进行转换，获取指定资源id对应的尺寸，返回值类型为float。转换规则如下：
```
switch (unit) {
        case COMPLEX_UNIT_PX:
            return value;
        case COMPLEX_UNIT_DIP:
            return value * metrics.density;
        case COMPLEX_UNIT_SP:
            return value * metrics.scaledDensity;
        case COMPLEX_UNIT_PT:
            return value * metrics.xdpi * (1.0f/72);
        case COMPLEX_UNIT_IN:
            return value * metrics.xdpi;
        case COMPLEX_UNIT_MM:
            return value * metrics.xdpi * (1.0f/25.4f);
        }
```
它的返回值其实就是像素大小，但为浮点数而已。

- getDimensionPixelSize：将getDimension的结果四舍五入为整数。
- getDimensionPixelOffset：将getDimension的结果的小数部分舍去，化为整数。

可见这三个方法的结果是非常相近的，差异一个像素不到，基本可以忽略。

如果我们是把字体的大小配置在dimen.xml文件中，然后通过Resources.getDimension来获取的，则我们需要这样设置字体的大小：
```
TextView.setTextSize(TypedValue.COMPLEX_UNIT_PX, res.getDimension(R.dimen.textsize));
```
我们需要指定字体单位为像素，因为我们通过getDimension获取的值的单位为像素。