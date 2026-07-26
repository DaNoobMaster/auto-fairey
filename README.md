# Auto-Fairey
This is a program created to help citizens pay a fair price for their auto. It allows users to input 2 locations and get the fair auto pricing for travel between them. Users may also optionally input the lenght of the journey ( to account for traffic in calculations) and extra baggage weight brought along. As of now the program does not include any prebuilt traffic caluclation and rather depends on calculating the difference betweeen the real travel time and predicted travel time to account for traffic.
KEEP IN MIND - The program uses system clock to calculate whether the fare will be a night-fare or normal fare.
Currently, as the program requires internet and the pricing works as per Bangalore, users are given the option to enter their own auto fare details for their city. This will later be changed to become autonomous instead.
Installation steps : 
1. Clone the github directory

       git clone https://github.com/DaNoobMaster/auto-fairey/
  
2. Navigate to the project directory.

       cd auto-fairey

3. Create a virtual environment.

       python3 -m venv auto-fairey

4. Activate the virtual environment.

   On Windows :
   
       auto-fairey\Scripts\activate
   
   On MacOS/Linux :
   
       source auto-fairey/bin/activate

5. Install all dependencies

       pip install -r requirements.txt

6. Run the application

       python main.py

   <img width="486" height="182" alt="image" src="https://github.com/user-attachments/assets/ad5f6428-c047-4ac3-a415-82d0531d92b1" />

