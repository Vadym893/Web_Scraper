import matplotlib.pyplot as plt
def chart_Data(object):
    def pie_data():
        recommend_counter={"Recommended":0, "Not Recommended":0}
        for  key, value in object.items():
                if value["Recommend"][0]!="\nNie polecam\n":
                    recommend_counter["Recommended"]+=1
                elif value["Recommend"][0]!="\nPolecam\n":
                    recommend_counter["Not Recommended"]+=1
        print(recommend_counter)
        plt.pie(recommend_counter.values(), labels=recommend_counter.keys(), autopct='%1.1f%%', startangle=140)
        plt.title('Share of Recommendations')
        plt.savefig('static/pie_chart.png')
        plt.close()
        
    def  bar_data():
        obj={"0/5":0,"0,5/5":0,"1/5":0,"1,5/5":0,"2/5":0, "2,5/5":0, "3/5":0,"3,5/5":0,"4/5":0, "4,5/5":0, "5/5":0}
        for  key, value in object.items():
            for  k, v in obj.items():
                if k==value["Rating"]:
                    obj[k]+=1
        print(obj)
        plt.bar(obj.keys(), obj.values())
        plt.xlabel('Star Rating')
        plt.ylabel('Number of Opinions')
        plt.title('Number of Opinions by Star Rating')
        plt.savefig('static/bar_chart.png')
        plt.close()
    pie_data()
    bar_data()