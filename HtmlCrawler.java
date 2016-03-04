import java.io.BufferedReader;
import java.io.FileWriter;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class HtmlCrawler {
	
	public static void main(String[] args) throws Exception {
		String htmlstr=getStringByUrl("http://tech.sina.com.cn");
		String cstart="<div style=\"display:none!important;height:0!"+
				"important;overflow:hidden!important;\">";
		String cend="<!-- 返回顶部 begin -->";
		String parsestr="(<h2><a href=\"(.*?)\" target=\"_blank\">(.*?)</a>"+
					"[\\s\\S]*?class=\"npt\">(.*?)</a>[\\s\\S]*?"+
					"<div class=\"time\">(.*?)</div>)";
		
		
		String HTMLContent=getHTMLContent(htmlstr,cstart,cend);
		
		boolean re=save2File(parseHTML(HTMLContent,parsestr));
		System.out.println(re==true?"success":"fail");
		
	}
	//通过URL获得网页
	public static String getStringByUrl(String strurl)
    {
      StringBuilder htmlstr=new StringBuilder();
      try {
			URL url=new URL(strurl);
			HttpURLConnection uc=(HttpURLConnection)url.openConnection();
			InputStream is=uc.getInputStream();
			BufferedReader br=new BufferedReader(new InputStreamReader(is,"utf-8"));
			String str=null;
			while(null!=(str=br.readLine()))
			{
				htmlstr.append(str+"\n");
			}
			br.close();
	   } catch (Exception e) {
		   e.printStackTrace();
	   }
       return htmlstr.toString();
    }
	//截取内容
	public static String getHTMLContent(String htmlstr,String startexp,String endexp){
		int contentstart=0,contentend=0;
		
		Pattern cpstart=Pattern.compile(startexp);
        Matcher cm=cpstart.matcher(htmlstr);
        while(cm.find()){
        	contentstart=cm.end();
        }
        
		Pattern cpend=Pattern.compile(endexp);
        cm=cpend.matcher(htmlstr);
        while(cm.find()){
        	contentend=cm.end();
        }
        htmlstr=htmlstr.substring(contentstart, contentend);
		return htmlstr;
	}
	//得到文章列表
	public static ArrayList<Article> parseHTML(String htmlstr,String parsestr){
		ArrayList<Article> list=new ArrayList<Article>();
		Pattern pattern=Pattern.compile(parsestr);
		Matcher urlmc=pattern.matcher(htmlstr);
		int index=0;
		int id=1;
		while(urlmc.find(index))
		{
			Article article=new Article(id++, urlmc.group(2),
					urlmc.group(3),urlmc.group(5),urlmc.group(4));
			
			article.setContent(getArticleContent(urlmc.group(2)));
			list.add(article);
			index=urlmc.end();
		}
		return list;
	}
	//删除Html标签     
    public static String getTextFromHtml(String str){
    	str=str.replaceAll("<div class=\"img_wrapper\">[\\s\\S]*?</span></div>", "");
		str=str.replaceAll("<[^>]+>", "");
		str=str.replaceAll("&nbsp;", "");
		return str.trim();
    }
    //得到文章内容
	public static String getArticleContent(String url){
		String articlestr=getStringByUrl(url);
		String articleStartexp="<div class=\"content\" "+
					"id=\"artibody\" data-sudaclick=\"blk_content\">";
		String articleEndexp="<!-- 正文页左下画中画广告 begin -->";
		String articleContent=getHTMLContent(articlestr,articleStartexp,articleEndexp);
		return getTextFromHtml(articleContent.substring(0, articleContent.length()));
	}
	//保存到数据库
	public static boolean save2Db(ArrayList<Article> list){
		boolean re=false;
		
		Iterator<Article> it=list.iterator();
		while(it.hasNext()){
			System.out.println(((Article)it.next()).display());
		}
		
		return re;
	}
	//保存到文件
		public static boolean save2File(ArrayList<Article> list){
			boolean re=false;
			
			try {
				FileWriter fw=new FileWriter("e:\\tech_news_list.txt");
				Iterator<Article> it=list.iterator();
				while(it.hasNext()){
					String str=((Article)it.next()).display();
					fw.write(str);
				}
				fw.close();
				re=true;
			} catch (IOException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
			return re;
		}
}
