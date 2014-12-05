<script type="text/javascript">
// <![CDATA[
$(document).ready(function(){
    var new_filter = "";
    groups = "<ul>";
    $("select#id_group_by option").each(function(){
        groups += "<li><a href='#'>"+$(this).text()+"</a></li>";
    });
    groups += "</ul>";
    $("#groupbychoices").html(groups);
    $("table.report_content tbody tr td:first-child").css("cursor", "pointer");
    $("table.report_content tbody tr td:first-child").click(function(){
       // get selected item
       var field_name = $("table.report_content thead tr td:first").text();
       /*if ((field_name == 'Date') && $('#id_Days').attr('name') == 'Days'){
          field_name = 'Days';
          //alert("estoy dentro");
       }*/
       new_filter = field_name + '=' + $(this).attr("id");

       $("#groupbychoices ul li a").each(function(){
         var url = document.location.href;
         // get clicked url
         var group_selected = $(this).text();
         if (url.search('group_by') == -1){
             url += '?group_by=';
             url += group_selected;
             url = url + '&' + new_filter;
     	     url = url.replace(' ', '+');
	     url += '&form_submitted=1&submit=Submit+Query';
             $(this).attr("href", url);
         }
         else{
             // get selected group
             var previous_selected = $("select#id_group_by option:selected").text();
             var old_group = 'group_by=' + previous_selected;
             url = url.replace(old_group, 'group_by='+group_selected);
             url = url + '&' + new_filter;
	     url = url.replace(' ', '+');
             $(this).attr("href", url);
         }
       
       });
       




        $.openDOMWindow({
             windowSourceID: '#groupBys',
             width: 150,
             height: 150
        });
        return false;
    });
});
// ]]>
</script>
