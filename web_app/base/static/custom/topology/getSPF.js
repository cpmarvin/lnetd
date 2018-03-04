function getSPF(source,target){
	links_spf = []
	links.forEach(function(d) { links_spf.push({source:d.source.name,target:d.target.name,metric:d.metric,id:d.link_id}) })
	var arrStr = encodeURIComponent(JSON.stringify(links_spf));
	url = "http://X.X.X.X:8801/api/spf?"+"arr="+arrStr+"&"+"source="+source+"&"+"target="+target
	var spf_results = $.ajax({type: "GET", url: url, async: false}).responseJSON;
	return { spf_results}
}
