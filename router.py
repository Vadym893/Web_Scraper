from flask import Flask,render_template,redirect,flash,url_for,request,send_file,make_response
from project import backend
from form import Id_Form,Chart_check,Graph_exit
import os
import json
import io
import operator
import csv
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
all_search={}
history_info={}
SECRET_KEY = os.urandom(32)
app = Flask(__name__)
app.config["SECRET_KEY"]=SECRET_KEY
product_id_arr=[]
def data_scrap(id):
    if id in all_search:
        return all_search[id]
    # Perform data scraping
    result = backend(id)
    # Cache the result
    all_search[id] = result
    return result
def history_data(all_search):
    for key,value in all_search.items():
        if value!=False:
            advantage_sum=0
            disadvantage_sum=0
            total_comments=0
            total_score=0
            for k,v in value.items():
                total_comments+=1
                if v["Advantages"]:
                    advantage_sum += 1
        
                if v["Disadvantages"]:
                    disadvantage_sum += 1
                score_str = v["Rating"].replace(',', '.')  # Convert to float
                score = float(score_str.split('/')[0])
                total_score += score
            history_info[key]= {"amount_of_comments": total_comments,"amount_of_advantages":advantage_sum,"amount_of disadvantages":disadvantage_sum,"Average_rating":round(total_score/total_comments,2) if total_comments!=0 else 0}
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
if __name__ == '__main__':
    app.run(debug=True)
@app.route('/')

@app.route('/home')
def index():
    return render_template('home.html')

@app.route('/search',methods=['GET','POST'])
def search():
    form =Id_Form()
    if request.method == 'POST':
        product_id = request.form["id"]
        if form.validate_on_submit():
            flash("request submitted","success")
            product_id_arr.append(product_id)
            return redirect(url_for("reviews",product_id=product_id))
    return render_template('search.html',form=form)

@app.route(f'/reviews/<product_id>',methods=['GET','POST'])
def reviews(product_id):
    form =Chart_check()
    if (data_scrap(product_id))!=False:
        sort_by = request.args.get('sort_by')
        filter_by = request.args.get('filter_by')
        page_number = request.args.get('page', default=1, type=int)
        reviews_per_page = int(request.args.get('comments_per_page', 10))
        start_index = (page_number - 1) * reviews_per_page
        end_index = start_index + reviews_per_page
        if sort_by == 'date':
            sorted_reviews = sorted(all_search[product_id].items(), key=lambda x: x[1]['Published'])
        elif sort_by == 'rating':
            sorted_reviews = sorted(all_search[product_id].items(), key=lambda x: x[1]['Rating'])
        else:
            # Default sorting
            sorted_reviews = all_search[product_id].items()

        # Filter reviews based on the chosen criteria
        if filter_by == '5_stars':
            filtered_reviews = {key: value for key, value in sorted_reviews if value['Rating'] == '5/5'}
        elif filter_by == 'recommend':
            filtered_reviews = {key: value for key, value in sorted_reviews if '\nPolecam\n' in value['Recommend']}
        else:
            # Default filtering
            filtered_reviews = dict(sorted_reviews)
        reviews = {name: values for name, values in filtered_reviews.items() if start_index <= list(filtered_reviews.keys()).index(name) < end_index}
        if request.method == 'POST':
            if form.validate_on_submit():
                return redirect(url_for("charts",product_id=product_id))
        return render_template('review.html',form=form,page=reviews,product_id=product_id,length=len(all_search[product_id]),per_page=reviews_per_page,page_number=page_number,sort_by=sort_by,filter_by=filter_by)
    else:
        return render_template('review.html',form=form,page=all_search[product_id],product_id=product_id)
@app.route(f'/charts/<product_id>',methods=['GET','POST'])
def charts(product_id):
    form = Graph_exit()
    if request.method == 'POST':
        if form.validate_on_submit():
            return redirect(url_for("reviews",product_id=product_id))
    chart_Data(all_search[product_id])
    return render_template("chart.html",form=form)

@app.route('/history')
def history():
    history_data(all_search)
    return render_template("history.html",data=history_info)

@app.route('/author')
def author():
    return "here will be author page"

@app.route('/download',methods=['GET','POST'])
def download():
    product_id = request.args.get('id')
    format = request.args.get('format')
    if format=="csv":
        csv_output = io.StringIO()
        fieldnames = [ 'Id', 'Published', 'Usage_time', 'Author', 'Text', 'Rating', 'Likes', 'Dislikes',
                    'Recommend', 'Advantages', 'Disadvantages', 'Comments']
        for  i in range (history_info[product_id]["amount_of_comments"]+1):
            fieldnames.append(f"Review{i}")
        csv_writer = csv.DictWriter(csv_output, fieldnames=fieldnames)
        
        # Write CSV header
        csv_writer.writeheader()
        
        # Write data rows to CSV
        for review_id, review_data in all_search.items():
            csv_writer.writerow({k: v if isinstance(v, str) else ','.join(v) for k, v in review_data.items()})
        
        # Set the position to the beginning of the StringIO object
        csv_output.seek(0)
        
        # Create a response object with the CSV data
        response = make_response(csv_output.getvalue())
        
        # Set headers to force browser download
        response.headers['Content-Disposition'] = 'attachment; filename=reviews.csv'
        response.headers['Content-type'] = 'text/csv'
    
        return response
    elif format=="json":
            if product_id in all_search:
                product = all_search[product_id]
                
                # Convert product data to JSON format
                json_data = json.dumps(product)
                
                # Serve the JSON data for download
                return send_file(io.BytesIO(json_data.encode()), as_attachment=True, download_name=f"{product_id}.json")
            else:
                return "Product not found"
    elif format=="xlsx":
            if product_id in all_search:
                product = all_search[product_id]
                # Create a DataFrame
                df = pd.DataFrame(product)
                excel_output = io.BytesIO()
                with pd.ExcelWriter(excel_output, engine='xlsxwriter') as writer:
                    df.to_excel(writer, index=False, sheet_name='Sheet1')
                
                # Serve the Excel file for download
                excel_output.seek(0)
                return send_file(excel_output, as_attachment=True, download_name=f"{product_id}.xlsx")
            else:
                return "Product not found"
if __name__ == '__main__':
    app.run(debug=True)
   