import streamlit as st

def show_privacy_policy():
    """Display privacy policy page"""
    st.title("🔒 Privacy Policy")
    st.markdown("*Last updated: July 26, 2025*")
    
    st.markdown("""
    ## Introduction
    
    This Privacy Policy describes how Data Chatbot Agent ("we", "our", or "us") collects, uses, and protects your information when you use our service.
    
    ## Information We Collect
    
    ### Data You Upload
    - CSV files, JSON files, SQL databases, and other data files you choose to upload
    - Database connection parameters you provide (stored temporarily during your session)
    - Queries and questions you ask about your data
    
    ### Automatically Collected Information
    - Usage analytics through Google Analytics (pages visited, session duration, features used)
    - Technical information (browser type, device type, IP address)
    - Cookies for advertising and analytics purposes
    
    ## How We Use Your Information
    
    ### Primary Uses
    - Process your data queries and provide responses
    - Improve our AI models and service quality
    - Generate usage analytics to enhance user experience
    - Display relevant advertisements through Google AdSense
    
    ### Data Processing
    - Your uploaded data is processed in-memory and not permanently stored
    - Database connections are temporary and closed after your session
    - Query history is stored locally in your browser session only
    
    ## Third-Party Services
    
    ### Google AdSense
    - We use Google AdSense to display advertisements
    - Google may use cookies to show relevant ads based on your interests
    - You can opt out of personalized advertising at [Google Ad Settings](https://adssettings.google.com/)
    
    ### Google Analytics
    - We use Google Analytics to understand how users interact with our service
    - Analytics data is aggregated and anonymized
    - You can opt out using browser plugins or settings
    
    ### OpenRouter.ai
    - We use OpenRouter.ai for AI-powered query processing
    - Your queries are sent to OpenRouter.ai but are not stored permanently
    - OpenRouter.ai has its own privacy policy governing data handling
    
    ## Data Security
    
    ### Protection Measures
    - All data transmission is encrypted using HTTPS
    - Uploaded files are processed in-memory only
    - No permanent storage of your sensitive data
    - Database connections are secured and temporary
    
    ### Data Retention
    - Uploaded files: Deleted when you close your browser session
    - Query history: Stored locally in your browser only
    - Analytics data: Retained by Google Analytics according to their policies
    
    ## Your Rights
    
    ### Data Control
    - You can clear your chat history at any time using the "Clear Chat History" button
    - You can disable cookies in your browser settings
    - You can opt out of Google Analytics tracking
    - You control what data you choose to upload
    
    ### Access and Deletion
    - Your uploaded data is automatically deleted when your session ends
    - To request deletion of any analytics data, contact us
    - You have the right to know what data we have about you
    
    ## Cookies and Tracking
    
    ### Types of Cookies
    - **Essential Cookies**: Required for basic service functionality
    - **Analytics Cookies**: Google Analytics for usage tracking
    - **Advertising Cookies**: Google AdSense for relevant ad display
    - **Session Cookies**: Temporary cookies for your browsing session
    
    ### Managing Cookies
    - You can disable cookies in your browser settings
    - Disabling essential cookies may affect service functionality
    - Advertising cookies can be managed through Google Ad Settings
    
    ## Children's Privacy
    
    Our service is not intended for children under 13. We do not knowingly collect personal information from children under 13. If you are a parent and believe your child has provided us with personal information, please contact us.
    
    ## International Users
    
    Our service is hosted and operated from various global locations. By using our service, you consent to the transfer of your information to countries that may have different data protection laws than your country.
    
    ## Changes to Privacy Policy
    
    We may update this Privacy Policy from time to time. We will notify users of any material changes by updating the "Last updated" date at the top of this policy. Continued use of the service after changes constitutes acceptance of the updated policy.
    
    ## Contact Information
    
    If you have questions about this Privacy Policy or our data practices, please contact us:
    
    - **Email**: [Your Email Address]
    - **Website**: [Your Website URL]
    - **Address**: [Your Business Address]
    
    ## Compliance
    
    This privacy policy is designed to comply with:
    - General Data Protection Regulation (GDPR)
    - California Consumer Privacy Act (CCPA)
    - Google AdSense Program Policies
    - Google Analytics Terms of Service
    
    By using our service, you acknowledge that you have read and understood this Privacy Policy.
    """)

if __name__ == "__main__":
    show_privacy_policy()