import streamlit as st
import pandas as pd
import plotly.express as px

class SurveyAnalysis:

    def __init__(self):
        self.df = self.load_data()
        self.process_data()

    @staticmethod
    def load_data():
        return pd.read_csv('source/data.csv')

    def process_data(self):
        self.df['Estimated Salary'] = self.df['Maaş / Aylık Türk Lirası cinsinden'].apply(self.estimate_average_salary)
        self.total_respondents = self.df.shape[0]
        self.most_common_benefits = self.df['Yan haklarınız'].str.split('\n').explode().value_counts().head(5)
        self.gender_counts = self.df['Cinsiyet'].value_counts().reset_index()
        self.gender_counts.columns = ['Cinsiyet', 'Count']
        self.work_type_counts = self.df['Çalışma şekliniz nedir?'].value_counts().reset_index()
        self.work_type_counts.columns = ['Çalışma şekliniz nedir?', 'Count']

        self.technologies = self.df['Ağırlıklı olarak hangi teknolojileri / dilleri kullanıyorsunuz?'].str.split('\n').explode().value_counts().reset_index()
        self.technologies.columns = ['Technology', 'Count']
        self.avg_salary_by_position = self.df.groupby('Seviyeniz nedir?')['Estimated Salary'].mean().reset_index()

        self.avg_salary_by_position_level = self.df.groupby(['Hangi pozisyonda çalışıyorsunuz?', 'Seviyeniz nedir?'])['Estimated Salary'].mean().reset_index()

        self.avg_salary_by_experience_level = self.df.groupby(['Deneyim', 'Seviyeniz nedir?'])['Estimated Salary'].mean().reset_index()

    @staticmethod
    def estimate_average_salary(salary_range):
        if "-" in salary_range:
            lower, upper = salary_range.split('-')
            lower = int(lower.replace('TL', '').replace('.', '').strip())
            upper = int(upper.replace('TL', '').replace('.', '').strip())
            return (lower + upper) / 2
        elif "ve altı" in salary_range:
            return int(salary_range.replace('TL', '').replace('ve altı', '').replace('.', '').strip())
        elif "ve üzeri" in salary_range:
            return int(salary_range.replace('TL', '').replace('ve üzeri', '').replace('.', '').strip())
        else:
            return int(salary_range.replace('TL', '').replace('.', '').strip())
        
    def benefits_distribution(self):
        return px.bar(self.most_common_benefits, x=self.most_common_benefits.index, y=self.most_common_benefits.values, title='En Yaygın 5 Yan Hak', height=400)

    def get_visualization(self, option):
        if option == "Cinsiyete Göre Dağılım":
            return px.pie(self.gender_counts, names='Cinsiyet', values='Count', title='Cinsiyete Göre Dağılım', hover_data=['Count'], height=400)

        elif option == "Şehirlere Göre Dağılım":
            return px.histogram(self.df, x='Şirketiniz hangi şehirde? (Eğer Türkiye ise)', title='Şehirlere Göre Dağılım', height=400)

        elif option == "Çalışma Şekline Göre Dağılım":
            return px.pie(self.work_type_counts, names='Çalışma şekliniz nedir?', values='Count', title='Çalışma Şekline Göre Dağılım', hover_data=['Count'], height=400)

        elif option == "Seviyeye Göre Ortalama Maaşlar":
            return px.bar(self.avg_salary_by_position, x='Seviyeniz nedir?', y='Estimated Salary', title='Pozisyona Göre Ortalama Maaşlar', height=400)
        
        elif option == "Pozisyona ve Seviyeye Göre Ortalama Maaşlar":
            return px.bar(self.avg_salary_by_position_level, x='Hangi pozisyonda çalışıyorsunuz?', y='Estimated Salary', color='Seviyeniz nedir?', title='Pozisyona ve Seviyeye Göre Ortalama Maaşlar', height=400)
                
        elif option == "En Yaygın 5 Yan Hak":
            return self.benefits_distribution()

        elif option == "Meslek Kırılımları - Teknoloji/Dil Kullanımı":
            return px.bar(self.technologies, x='Technology', y='Count', title='Meslek Kırılımları - Teknoloji/Dil Kullanımı', height=400)

    
def display_interface():
    survey = SurveyAnalysis()
    
    st.title("Yazılımcı Maaş Anket Sonuçları")
    
    st.write(f"""
    Bu anket, yazılımcıların maaş ve çalışma koşulları hakkında bilgi almak amacıyla düzenlenmiştir.
    Toplam {survey.total_respondents} kişi ankete katılmıştır. 
    """)

    st.markdown("Bu anketin gerçekleştirilmesinde emeği geçen [Altuğ Akgül](https://twitter.com/altugakgul?s=21)'e teşekkür ederiz.")
    
    st.image("source/image.jpeg", caption="BT / Yazılım Sektörü")

    st.subheader("Görsel Analizler")
    
    st.markdown("""
    **Not:** Bu görsel analizler, ankete katılanların verdiği cevaplara dayanmaktadır. Veri setinde aykırı değerler olabileceği gibi, gerçeği tam anlamıyla yansıtmayan bazı maaş sonuçları da olabilir. Sonuçları değerlendirirken bu hususları göz önünde bulundurmanızı öneririz.
    """)
    
    visualization_option = st.sidebar.selectbox(
        "Hangi görselleştirmeyi görmek istersiniz?",
        ("Cinsiyete Göre Dağılım", 
         "Şehirlere Göre Dağılım", 
         "Çalışma Şekline Göre Dağılım", 
         "Seviyeye Göre Ortalama Maaşlar", 
         "Pozisyona ve Seviyeye Göre Ortalama Maaşlar",
         "En Yaygın 5 Yan Hak",
         "Meslek Kırılımları - Teknoloji/Dil Kullanımı"
        )
    )

    fig = survey.get_visualization(visualization_option)
    st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    st.set_page_config(page_title="Yazılımcı Maaş Anket Sonuçları", page_icon="source/logo.png")
    display_interface()