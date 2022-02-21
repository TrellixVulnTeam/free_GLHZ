/*
 * Activity 1.3.7
*/
class Shape
{
  String shapeOf="";
  int numOfSides;
  
  public void setShape(String x, int y)
  {
    shapeOf=x;
    numOfSides = y;
  }
  
  public String getShape()
  {
    return shapeOf;
  }
  
  public int getSides()
  {
    return numOfSides;
  }
  
  
  public boolean equals(Shape s)
  {  if (s != null) {
     if (s.shapeOf.equals(shapeOf) && s.numOfSides == numOfSides)
     {
       return true;
     }
     return false;
  }
  else{
    return false;
  }
}
}