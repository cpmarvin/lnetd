function getSPF(source,target){
        links_spf = []
        links.forEach(function(d) { links_spf.push({source:d.source.name,target:d.target.name,metric:d.metric,id:d.link_id,latency:d.latency}) 
})
        console.log("getSPF_fct array:" +links_spf[0]) 
        var arrStr = encodeURIComponent(JSON.stringify(links_spf));
        url = "http://<change-me>:8801/api/spf_and_latency?"+"arr="+arrStr+"&"+"source="+source+"&"+"target="+target
        var spf_results = $.ajax({type: "GET", url: url, async: false}).responseJSON;
        return { spf_results }
}
