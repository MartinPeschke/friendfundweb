function sprache()
{
document.getElementById('sprache').style.display='block';
window.setTimeout("sprache_off_timer()", 5000);
return false;
}
function sprache_off(element, evt)
{
el = document.getElementById('sprache');
if (element.contains && evt.toElement)
{
to = evt.toElement
if (!element.contains(to) && to.id != "sprache")
{
el.style.display="none";
}
}
else if (evt.relatedTarget)
{
el.style.display="none";
}
}
function sprache_off_timer()
{
document.getElementById('sprache').style.display='none';
}
function showsub(id, maxh)
{
el = document.getElementById("sub_"+id);
el.style.height = "0";
el.style.display = "block";
setTimeout("raise('"+id+"', 0, "+maxh+")", 70);
}
function raise(id, height, maxh)
{
height = Math.min(height+5, maxh);
el = document.getElementById("sub_"+id);
el.style.height = height + "px";
if (height < maxh)
{
setTimeout("raise('"+id+"', "+height+", "+maxh+")", 70);
}
}
function getXMLObj()
{
var xmlHttpObject = false;
if (typeof XMLHttpRequest != 'undefined')
{
xmlHttpObject = new XMLHttpRequest();
}
if (!xmlHttpObject)
{
try
{
xmlHttpObject = new ActiveXObject("Msxml2.XMLHTTP");
}
catch(e)
{
try
{
xmlHttpObject = new ActiveXObject("Microsoft.XMLHTTP");
}
catch(e)
{
xmlHttpObject = null;
}
}
}
return xmlHttpObject;
}
var suche_w = null;
var suche_e = null;
function wortliste(s, dstdiv, par1)
{
if (!suche_w) suche_w = getXMLObj();
if (s.length >= 2)
{
if (suche_w.readyState == 1 || suche_w.readyState == 2 || suche_w.readyState == 3)
{
suche_w.abort();
}
suche_w.open("get","suche.html?words&par1="+par1+"&suche="+encodeURIComponent(s));
suche_w.setRequestHeader("Content-type", "application/x-www-form-urlencoded;charset=UTF-8");
suche_w.onreadystatechange = function()
{
if (suche_w.readyState == 4)
{
el = document.getElementById(dstdiv);
el.style.display = "block";
el.innerHTML=suche_w.responseText;
}
};
suche_w.send(null);
el = document.getElementById(dstdiv);
el.style.visibility = "visible";
el.innerHTML = "<p>...<\/p>";
}
else
{
el = document.getElementById(dstdiv);
el.style.visibility = "hidden";
}
}
function wortclick(w)
{
els = document.getElementById("suchwort");
els.value = w;
elw = document.getElementById("worte");
elw.style.display = "none";
suche(0);
return false;
}
function suche(offset)
{
if (!suche_e) suche_e = getXMLObj();
elw = document.getElementById("worte");
elw.style.display = "none";
els = document.getElementById("suchwort");
s = els.value;
if (s.length >= 3)
{
el = document.getElementById("teilsuche");
suche_e.open("get","suche.html?incremental&offset="+offset+"&suche="+encodeURIComponent(s));
suche_e.setRequestHeader("Content-type", "application/x-www-form-urlencoded;charset=UTF-8");
suche_e.onreadystatechange = function()
{
if (suche_e.readyState == 4)
{
el = document.getElementById("teilsuche");
el.style.display = "block";
el.innerHTML=suche_e.responseText;
}
};
suche_e.send(null);
el.style.display = "block";
el.innerHTML = "<p><img src='gr/warten.gif' style='vertical-align:middle;'> ...<\/p>";
}
return false;
}
var finder_preis = "";
var finder_region = "";
var finder_kategorie = "";
var finder_kategorie2 = "";
$(document).ready(function() {
s = $('#selectPreis').selectbox( { onChangeCallback: finderChangeP } );
s = $('#selectRegion').selectbox( { onChangeCallback: finderChangeR } );
s = $('#selectKategorie').selectbox( { onChangeCallback: finderChangeZ } );
s = $('#selectKategorie2').selectbox( { onChangeCallback: finderChangeK } );
s = $('#selectHotel').selectbox( { onChangeCallback: finderChange } );
$(".rand_navi li.inactive .inner").hide();
$("#selectRegion_container").css("height", "180px");
$("#selectPreis_container").css("height", "auto");
$("#selectKategorie_container").css("height", "160px");
$("#selectKategorie2_container").css("height", "130px");
$("#selectHotel_container").css("height", "auto");
finderChange();
});
function finderChangeP(sel) { finder_preis = sel.selectedVal; finderChange(); }
function finderChangeR(sel) { finder_region = sel.selectedVal; finderChange(); }
function finderChangeZ(sel) { finder_kategorie = sel.selectedVal; finderChange(); }
function finderChangeK(sel) { finder_kategorie2 = sel.selectedVal; finderChange(); }
function finderChange()
{
$("#finder_anzahl").load("http://www.meventi.de/finder.html?cnt&selectPreis="+finder_preis+"&selectRegion="+finder_region+"&selectKategorie="+finder_kategorie+"&selectKategorie2="+finder_kategorie2);
}
function tour()
{
$("#dialog").load("tour.html?frame");
$("#dialog").dialog({ dialogClass: 'meventiTour', width: 600, height:602, modal: 1, resizable: false, position: ['center','top'], title: 'meventi tour'} );
} 