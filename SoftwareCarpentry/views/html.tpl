%#template to generate a HTML table from a list of tuples (or list of lists, or tuple of tuples or ...)
<p>Displaying CSV file as HTML Table:</p>
<table border="1">
%for row in rows:
  <tr>
  %for col in row:
    <td>{{col}}</td>
  %end
  </tr>
%end
</table>
