public class Article{
	private int id;
	private String url;
	private String title;
	private String date;
	private String intr;
	private String content;
	public Article(int id,String url,String title,String date,String intr){
		this.id=id;
		this.url=url;
		this.title=title;
		this.date=date;
		this.intr=intr;
	}
	public String introduce(){
		return "Id:"+this.id+"\n"+
				"标题："+this.title+"\n"+
				"简介："+this.intr+"\n"+
				"时间："+this.date+"\n"+
				"URL："+this.url+"\n";
	}
	public String display(){
		return "Id:"+this.id+"\n"+
				"标题："+this.title+"\n"+
				"简介："+this.intr+"\n"+
				"时间："+this.date+"\n"+
				"URL："+this.url+"\n\n"+
				"内容："+this.content+
				"\n===================="+
				"===================="+
				"====================\n";
	}
	public String getContent() {
		return content;
	}
	public void setContent(String content) {
		this.content = content;
	}
	public int getId() {
		return id;
	}
	public void setId(int id) {
		this.id = id;
	}
	public String getUrl() {
		return url;
	}
	public void setUrl(String url) {
		this.url = url;
	}
	public String getTitle() {
		return title;
	}
	public void setTitle(String title) {
		this.title = title;
	}
	public String getDate() {
		return date;
	}
	public void setDate(String date) {
		this.date = date;
	}
	public String getIntr() {
		return intr;
	}
	public void setIntr(String intr) {
		this.intr = intr;
	}
}
