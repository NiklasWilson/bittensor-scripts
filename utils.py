"""_summary_
"""
import smtplib
from email.mime.text import MIMEText
import datetime
import os
import json

# import subprocess
import pexpect
import sys
import re
import time
from dotenv import load_dotenv
from string import Template


# Load the environment variables from the .env file
load_dotenv()

# Access the variables from the .env file
email_sender = os.getenv("EMAIL_SENDER")
email_recipients = json.loads(os.getenv("EMAIL_RECIPIENTS"))
email_password = os.getenv("EMAIL_PASSWORD")
WALLET_NAME = os.getenv("WALLET_NAME")
WALLET_PASSWORD = os.getenv("WALLET_PASSWORD")
SUBTENSOR_ENDPOINT = "ws://209.137.198.70:9944"  # TOOD: Move to .env

wallet_overview_command = Template(f"btcli wallet overview --wallet.name {WALLET_NAME}")
unstake_token_command = Template(
    f"btcli stake remove --wallet.name {WALLET_NAME} --wallet.hotkey $wallet_hotkey --max_stake 1 --subtensor.network local --subtensor.chain_endpoint {SUBTENSOR_ENDPOINT}"
)


class Utils(object):
    """_summary_

    Args:
        object (_type_): _description_
    """

    def __init__(self):
        pass

    @staticmethod
    def send_email(subject: str, body: str) -> bool:
        """
        Sends an email with the given subject and body.

        Args:
            subject (str): The subject of the email.
            body (str): The body of the email.

        Returns:
            None

        Raises:
            SMTPException: If there is an error while sending the email.

        Examples:
            >>> Utils.send_email("Hello", "This is the body of the email.")
        """
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = email_sender
        msg["To"] = ", ".join(email_recipients)

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp_server:
            smtp_server.login(email_sender, email_password)
            smtp_server.sendmail(email_sender, email_recipients, msg.as_string())

        print(f"{datetime.datetime.now()} Message sent!")

        return True

    @staticmethod
    def is_integer(n):
        try:
            # Attempt to convert the string to an integer
            int(n)
            return True
        except ValueError:
            # If a ValueError is raised, the conversion failed, meaning the string is not an integer
            return False

    @staticmethod
    def get_wallet() -> dict | None:
        """
        Retrieves the wallet with the given name and password.

        Args:
            wallet_name: The name of the wallet.
            wallet_password: The password of the wallet.

        Returns:
            Wallet: The retrieved wallet.

        Examples:
            >>> utils = Utils()
            >>> wallet = utils.get_wallet("MyWallet", "password")
        """

        command = f"btcli w overview --wallet.name {WALLET_NAME}"

        wallet = {"miners": []}

        # try:
        #     output = subprocess.check_output(
        #         command, shell=True, stderr=subprocess.STDOUT, universal_newlines=True
        #     )
        #     print("Output:")
        #     print(output)
        # except subprocess.CalledProcessError as e:
        #     print(f"Error: {e}")

        output = """ 
                                                                      Wallet - 8thtry:5HTrCgoS2XgBzHx51tAQ8Wygrf4Q5pjuB5mwsct8zooff4Pt                                                                       
Subnet: 6                                                                                                                                                                                                    
COLDKEY  HOTKEY     UID  ACTIVE  STAKE(τ)     RANK     TRUST  CONSENSUS  INCENTIVE  DIVIDENDS  EMISSION(ρ)   VTRUST  VPERMIT  UPDATED  AXON  HOTKEY_SS58                                                     
8thtry   miner1322  158   False   0.00214  0.00395   0.99706    0.00391    0.00395    0.00000           17  0.00000            404854  none  5EJ2w6xFSGNdJKTtPHXSBnyvsx4YsnhQw9GPfDCFk6ju1A42                
8thtry   miner630   141   False   0.00214  0.00392   1.00000    0.00391    0.00392    0.00000           16  0.00000            407134  none  5G9gdBJmyUxQtM7EqPDupzwy1FQsz1e8Q3BZrMxMbh7bbLBK                
8thtry   miner1163  159   False   0.00214  0.00395   0.99336    0.00391    0.00395    0.00000           17  0.00000            404832  none  5DLEjwwjYokLjWW5wpVfEC4pCVWUGPPDGFgXUCT4uCTXoSYx                
8thtry   miner077   153   False   0.00214  0.00395   0.99251    0.00391    0.00395    0.00000           17  0.00000            405681  none  5Fc7uGqSF1CGVptnwzeqr627fTm4UkBqCC72sUxHb9km31Vt                
8thtry   miner1289  155   False   0.00214  0.00392   1.00000    0.00391    0.00392    0.00000           16  0.00000            405176  none  5GN73hDUXySte3Y6pTXB1C9bsgmrXG4YtxpV4nJVn84XUzZ6                
8thtry   miner2896  139   False   0.81491  0.00395   0.99500    0.00391    0.00395    0.00000           17  0.00000        *   407137  none  5GNeaf34G6xf7msQjd8LVD9dReMMN4ZGd8zBuGVy883k9fbZ                
8thtry   miner569   125   False   0.00214  0.00395   0.96162    0.00391    0.00395    0.00000           17  0.00000            408898  none  5Dvf7J43cprzZmSW4BiLKXX951gPkLC6JdyX26iYieGXEa6F                
8thtry   miner2647  142   False   0.00214  0.00383   1.00000    0.00391    0.00383    0.00000           16  0.00000            406776  none  5D9gy1rozwEKxtEobQUheN4sjgmrnKtUR6y23ZLuPPgsNS8e                
8thtry   miner707   151   False   0.00214  0.00395   0.96481    0.00391    0.00395    0.00000           17  0.00000            405689  none  5EF3gkJAt7nK2bYDsNPbM1rUUq2hjfWV8FgX9owsv4kqEEJK                
8thtry   miner989   149   False   0.00214  0.00395   1.00000    0.00391    0.00395    0.00000           17  0.00000            406041  none  5HGjLLUSwqmbzHHuwAzUfXfNQuTgM2d89VnGYNWDz9z4v3sw                
8thtry   miner794   144   False   0.05714  0.00395   0.96881    0.00391    0.00395    0.00000           17  0.00000            406769  none  5Hgu1usxEuZiZZLVY9jhMS5FMiUUknezH1UYRbXGXjtwqZ3j                
8thtry   miner250   126   False   0.00214  0.00395   0.98976    0.00391    0.00395    0.00000           17  0.00000            408895  none  5CDXPDFLEpk4W1hrT7ni5VGb9tFbgujRcFuDbd9AyUwimVbx                
8thtry   miner871   134   False   0.00214  0.00395   0.98389    0.00391    0.00395    0.00000           17  0.00000            407854  none  5C5qasgJwsFTz7boGEUzmNDnqW9ADdJd9xoe78pdkUfga5vj                
8thtry   miner360   133   False   0.00214  0.00394   1.00000    0.00391    0.00394    0.00000           17  0.00000            407855  none  5Ct83emzYj2PErHHLKbpzUkXFdb4h2RCgkaQgkXBo92HVf1c                
8thtry   miner960   124   False   0.00214  0.00386   1.00000    0.00391    0.00386    0.00000           16  0.00000            408899  none  5FtBiLJJcizicjzVU7CaECYvy1ojAFL8YjJbbPXmFzvtSu7W                
8thtry   miner1537  127   False   0.00214  0.00395   0.99258    0.00391    0.00395    0.00000           17  0.00000            408577  none  5GRN1t6iQnj44ZyHrToCzE5w3Z44ksAbLiZYc9aKNDDtzbyx                
8thtry   miner2333  138   False   0.00214  0.00386   1.00000    0.00391    0.00386    0.00000           16  0.00000            407495  none  5FBgo34t5jpze9yqTUkL7KL9w5iuqxG5uvQv66vYxLkHpDxQ                
8thtry   miner114   135   False   0.00214  0.00386   1.00000    0.00391    0.00386    0.00000           16  0.00000            407853  none  5CvexBxA5vBSLyZnhmTBEdqjfaahU9MW4K5ugyFy81ipePQx                
8thtry   miner1936  162   False   0.00214  0.00395   0.98419    0.00391    0.00395    0.00000           17  0.00000            404400  none  5GvVWtgRDHLrPG7XzA3Q79xjBphL8cWGGQ6FaocWSUx3HabX                
8thtry   miner1893  156   False   0.00214  0.00386   1.00000    0.00391    0.00386    0.00000           16  0.00000            405157  none  5CcBeirVNyQsKX4sC1bWQdcWNRyB362R93LhWFhVF8ng77Cp                
                    20                     0.07848  19.82359    0.07813    0.07848    0.00000         ρ333  0.00000                                                                                          
Subnet: 7                                                                                                                                                                                                    
COLDKEY  HOTKEY    UID  ACTIVE  STAKE(τ)     RANK    TRUST  CONSENSUS  INCENTIVE  DIVIDENDS  EMISSION(ρ)   VTRUST  VPERMIT  UPDATED  AXON                 HOTKEY_SS58                                        
8thtry   miner741  115   False   1.10664  0.00508  0.90306    0.00467    0.00508    0.00000       71_179  0.00000            400135  209.137.198.96:7741  5DV5AmHvtruMKirBaTU15625zLnjWxWyjbZ2vaRecqmnYb6f   
8thtry   miner789  26    False   1.02949  0.00136  0.33751    0.00163    0.00136    0.00000       19_078  0.00000            419372  209.137.198.95:7789  5DAYiD4gxXybjsJjs7M4xcdQ5cUWVmnprjTLRLJgWDih4Px5   
8thtry   miner725  47    False   1.08084  0.00409  0.92593    0.00386    0.00409    0.00000       57_292  0.00000            416776  209.137.198.89:7725  5ECf3PuqMGVFVKrQx6uxxwhtZHRQPwZBHSXMEBuTGCxGCx38   
8thtry   miner736  56    False   1.07537  0.00371  0.64291    0.00395    0.00371    0.00000       52_084  0.00000            415770  209.137.198.97:7736  5CXHGz12TGV5sNwvTcpxdCocNpZnna7PDLY3xU92sqr2PBwt   
8thtry   miner713  113   False   1.12936  0.00629  0.90159    0.00555    0.00629    0.00000       88_087  0.00000            400297  209.137.198.90:7713  5C88AYi93BHhMz478bwqKL2jVjnfhn87pusR4DoreHMJe56J   
8thtry   miner762  116   False   1.10746  0.00513  0.91098    0.00470    0.00513    0.00000       71_957  0.00000            399045  209.137.198.99:7762  5Cfmkt3tdEcKqQYwrRtJGexsjer1LhrmdDyFFbePH2SGaWFm   
8thtry   miner795  67    False   1.09154  0.00417  0.69827    0.00383    0.00417    0.00000       58_404  0.00000            413845  209.137.198.98:7795  5CCrTpDr5ZbFo5Mx7AMhAW8AvRVgdRhDQHn3KsoAJyAuaVSn   
8thtry   miner752  21    False   1.09817  0.00473  0.91351    0.00436    0.00473    0.00000       66_255  0.00000            419631  64.247.206.236:7752  5GsNb9mjMkeGNac2rYBvznqqA9kro5vhjjDXX9ouCStSZR2q   
8thtry   miner787  50    False   1.07893  0.00386  0.63694    0.00395    0.00386    0.00000       54_229  0.00000            416494  64.247.206.139:7787  5Fk2czYSppbsYPAkcLXh6eusEDYaygMNG7N7rGtWhk4gTxEd   
                   29                     0.03841  6.87071    0.03651    0.03841    0.00000     ρ538_565  0.00000                                                                                            
Subnet: 8                                                                                                                                                                                                    
COLDKEY  HOTKEY    UID  ACTIVE  STAKE(τ)     RANK    TRUST  CONSENSUS  INCENTIVE  DIVIDENDS  EMISSION(ρ)   VTRUST  VPERMIT  UPDATED  AXON                 HOTKEY_SS58                                        
8thtry   miner899  1     False   1.35767  0.00502  0.99805    0.00500    0.00502    0.00000      249_027  0.00000            129254  209.137.198.89:8899  5G6UKyE6SKDTSgVyCZvDhCSSYJNP3YX49326nojRuaycfR7k   
8thtry   miner848  178   False   1.36860  0.00517  0.99879    0.00516    0.00517    0.00000      256_346  0.00000            362306  209.137.198.98:8848  5DZgoQu6LFe6DYrcakBAhHXojmb9suHGsNiK4ZWnqaF7Zkup   
8thtry   miner877  185   False   0.08378  0.00134  0.97205    0.00134    0.00134    0.00000       66_945  0.00000            105500  209.137.198.98:8877  5CUQhTTApVCFHmEcNNJQJA81A81nXobVDLvvFCASDtCfG9ev   
8thtry   miner805  58    False   1.36707  0.00514  0.99858    0.00516    0.00514    0.00000      254_977  0.00000            407076  209.137.198.90:8805  5FJ8tx2rYEzAewcghU5tSJdGbceTWTntCtejjvGn3mz9bEFn   
8thtry   miner891  188   False   0.00000  0.00000  0.00000    0.00000    0.00000    0.00000            0  0.00000            357606  209.137.198.97:8910  5GEbv4UHTFCEzBMqjXKsP5T4xwU32UjLbDdgP7mA1M4QSmhZ   
8thtry   miner884  26    False   1.36650  0.00514  0.99840    0.00516    0.00514    0.00000      254_882  0.00000            414318  209.137.198.89:8884  5FbN7tJ5DzWpbuqaGJn9a6BFX51GgFJtAxkEyDRoUqfy4Mha   
8thtry   miner885  45    False   0.00000  0.00000  0.00000    0.00000    0.00000    0.00000            0  0.00000            176001  209.137.198.97:8850  5DniQz9rezzTFvcZ9z31nvrGyW9RruK5VEbjhMrT6xCJqouh   
                   36                     0.02182  4.96587    0.02182    0.02182    0.00000   ρ1_082_177  0.00000                                                                                            
Subnet: 14                                                                                                                                                                                                   
COLDKEY  HOTKEY     UID  ACTIVE  STAKE(τ)     RANK    TRUST  CONSENSUS  INCENTIVE  DIVIDENDS  EMISSION(ρ)   VTRUST  VPERMIT  UPDATED  AXON                  HOTKEY_SS58                                      
8thtry   miner1424  88     True   0.03724  0.00000  0.00000    0.00000    0.00000    0.00000            0  0.00000                45  209.137.198.89:14240  5FHurjo4t7gtYaatejhxmbZcFtQMkMF4CNgtnS8W9FaK41nL 
8thtry   miner1449  90     True   0.01337  0.02730  0.99300    0.02695    0.02730    0.00000       12_303  0.00000                71  209.137.198.90:14490  5Gbfo75i5rsm6BvqGfQQdpcXBibiwdNmnHwbBHGrYpChY7br 
                    38                     0.02730  0.99300    0.02695    0.02730    0.00000      ρ12_303  0.00000                                                                                           
Subnet: 15                                                                                                                                                                                                   
COLDKEY  HOTKEY     UID  ACTIVE  STAKE(τ)     RANK    TRUST  CONSENSUS  INCENTIVE  DIVIDENDS  EMISSION(ρ)   VTRUST  VPERMIT  UPDATED  AXON  HOTKEY_SS58                                                      
8thtry   miner1527  111   False   0.00000  0.00000  0.00000    0.00000    0.00000    0.00000            0  0.00000            301834  none  5GnXy7DTJELMCrcCWGbjW9bU3QGuQbfjx6RD3cPYe473pY8T                 
8thtry   miner1596  194   False   0.00000  0.00000  0.00000    0.00000    0.00000    0.00000            0  0.00000            159638  none  5CJpTf4ui5nEwLf7bHvVqBtFhMKo8Hhi1fvSEBddyASj7HNi                 
8thtry   miner1514  26    False   0.00000  0.00000  0.00000    0.00000    0.00000    0.00000            0  0.00000            318042  none  5CFqeMPLD5Db3q2kZdNnQswPBpmrB1NdqtAafxxGJ4R571dD                 
                    41                     0.00000  0.00000    0.00000    0.00000    0.00000           ρ0  0.00000                                                                                           
Subnet: 16                                                                                                                                                                                                   
COLDKEY  HOTKEY     UID  ACTIVE  STAKE(τ)     RANK    TRUST  CONSENSUS  INCENTIVE  DIVIDENDS  EMISSION(ρ)   VTRUST  VPERMIT  UPDATED  AXON                  HOTKEY_SS58                                      
8thtry   miner1649  72    False   0.07723  0.00479  0.83120    0.00429    0.00479    0.00000        3_736  0.00000            283853  209.137.198.91:16490  5Fpw7Fr86aenRwuse6zWm3LAhhK7iF1JmRChDQJfbwV2mjgW 
8thtry   miner1694  120   False   0.06766  0.00404  0.86870    0.00391    0.00404    0.00000        3_146  0.00000            208070  209.137.198.96:16940  5DXDnsKbBodEXfoZFoHTcdfmb4URbbeL87TwViZxM2qa1Wxt 
8thtry   miner1616  43    False   0.07865  0.00485  0.88594    0.00438    0.00485    0.00000        3_777  0.00000            300466  209.137.198.89:16160  5FRhX85Lmb7uY3GLjwaJBZeRRuUta1HHHiL5yXtV7mzH78d9 
8thtry   miner1631  232   False   0.06723  0.00476  0.75274    0.00424    0.00476    0.00000        3_707  0.00000            179499  209.137.198.95:16310  5FviPkmkSP7DVT7b2UZMCXGuH2wbJMhxwEV5Pwb85AuKR2Lp 
8thtry   miner1695  207   False   0.07457  0.00452  0.87817    0.00391    0.00452    0.00000        3_518  0.00000            184529  209.137.198.90:16950  5Dqex3kJbBWAfseEvExyBspYc6xpCsx6HHTs9tKLShUcExmX 
8thtry   miner1605  145   False   0.06384  0.00456  0.83297    0.00391    0.00456    0.00000        3_555  0.00000            192100  209.137.198.97:16050  5G6oUYvvdtfjBP6FganZ2tupNsGUbZ2HjaMY3s7q8gsBfLRC 
                    47                     0.02753  5.04973    0.02463    0.02753    0.00000      ρ21_439  0.00000                                                                                           
Subnet: 20                                                                                                                                                                                                   
COLDKEY  HOTKEY     UID  ACTIVE  STAKE(τ)     RANK    TRUST  CONSENSUS  INCENTIVE  DIVIDENDS  EMISSION(ρ)   VTRUST  VPERMIT  UPDATED  AXON  HOTKEY_SS58                                                      
8thtry   miner2051  171   False   0.00000  0.00505  0.99387    0.00499    0.00505    0.00000            0  0.00000            115726  none  5CLecXxG2nkNFroVgpx7mJMiHE4NmhKPJmKETDVBtW6qLGYJ                 
8thtry   miner2065  170   False   0.00000  0.00490  1.00000    0.00499    0.00490    0.00000            0  0.00000            115729  none  5ExsQBUQAW4oS7qx6MrZTXBZt6GW582rrjLwonuYNUFgBwcz                 
8thtry   miner2021  172   False   0.00000  0.00505  0.99803    0.00499    0.00505    0.00000            0  0.00000            113151  none  5HQgbmU2NM98d2GTaHUMiP2Sk4ZzkSYsEPKri46ejCETtq7F                 
8thtry   miner2090  169   False   0.00000  0.00505  0.96115    0.00499    0.00505    0.00000            0  0.00000            115732  none  5EgvbqAHi2gBHDZUuAHXxYjdKeqMbDXiTsk4z3GAHynJ8TKU                 
8thtry   miner2094  173   False   0.00000  0.00505  0.99330    0.00499    0.00505    0.00000            0  0.00000            113147  none  5CyaU6BHw2uNBFjxMvVTWidVzvcdXJN2BHNFfU5MLw6RQUUk                 
8thtry   miner2085  175   False   0.00000  0.00491  1.00000    0.00499    0.00491    0.00000            0  0.00000            108556  none  5E2DLkFpD7StjXrT97L71QnjbwVqs4A1udRBNoSkoSCgbdLh                 
8thtry   miner2041  174   False   0.00000  0.00505  0.99521    0.00499    0.00505    0.00000            0  0.00000            113143  none  5FbbmkDotHp166aqYftKVQU5qK3GE3fgebMtf7KTnhatwayG                 
8thtry   miner2029  176   False   0.00000  0.00488  1.00000    0.00499    0.00488    0.00000            0  0.00000            108552  none  5FyRauoAYWsqxL1uoDHcfzbVB4tMRNeBGv3swTqHGJtA97k4                 
8thtry   miner2076  177   False   0.00000  0.00505  0.99322    0.00499    0.00505    0.00000            0  0.00000            108549  none  5DwEohehVEZbZzqkqEwLvVST3Yq2D5dBrdnajwfGrF2bM9ZW                 
                    56                     0.04500  8.93478    0.04491    0.04500    0.00000           ρ0  0.00000                                                                                           
Subnet: 27                                                                                                                                                                                                   
COLDKEY  HOTKEY     UID  ACTIVE  STAKE(τ)     RANK    TRUST  CONSENSUS  INCENTIVE  DIVIDENDS  EMISSION(ρ)   VTRUST  VPERMIT  UPDATED  AXON                  HOTKEY_SS58                                      
8thtry   miner2745  191   False   1.06086  0.00211  0.80922    0.00217    0.00211    0.00000       40_988  0.00000            121267  64.247.206.236:27450  5Ey2cxpXcpMDd9hZBXLqtd4nq8mw6BhWhvjrukRMc4B89qPG 
8thtry   miner2744  165   False   1.08444  0.00294  0.90964    0.00388    0.00294    0.00000       57_098  0.00000            129188  209.137.198.97:27440  5E2WeKwWyjYjFeHx2T5paoRihxFf2bhQh6DeHxiuQjPfswF9 
8thtry   miner2710  164   False   1.09013  0.00310  0.88522    0.00388    0.00310    0.00000       60_043  0.00000            129669  209.137.198.96:27100  5HZH5euUVwUJJKEvHwpvo5hjDVXbcNfQnuC2kPTHSkDx7yfj 
8thtry   miner2762  189   False   1.10974  0.00359  0.92686    0.00394    0.00359    0.00000       69_469  0.00000            121982  64.247.206.139:27620  5DXWA8BK7SncFagXukwwNvxTiMYXZa6e12A2RVJqJ2Q1eMbP 
8thtry   miner2758  169   False   1.09774  0.00356  0.91344    0.00432    0.00356    0.00000       68_939  0.00000            128141  209.137.198.99:27580  5Hj5mqqdkmGwDiQmi5sahF9NouDpRWuCPawueWGmDdNfM6QL 
8thtry   miner2794  167   False   1.08327  0.00253  0.98361    0.00333    0.00253    0.00000       49_294  0.00000            129184  209.137.198.98:27940  5CJXjqRvSxQmVEQkdmEFjbKGz1qsPewLkM4GRdZAFwUZLjWS 
8thtry   miner2734  163   False   1.08699  0.00317  0.95831    0.00403    0.00317    0.00000       61_476  0.00000            129815  209.137.198.95:27340  5HVb8ZzRnXuWEaoVxc7PGwrbYvpyddodzUMFQUgyu5AK5JF5 
8thtry   miner2729  162   False   1.09617  0.00323  0.93391    0.00343    0.00323    0.00000       62_692  0.00000            129819  209.137.198.91:27290  5GRSYEHWRrPeRd88cECUsnHQtY6xL1JpoJ8FxYKh7AVEPJdJ 
8thtry   miner2765  53    False   1.05089  0.00224  0.94133    0.00316    0.00224    0.00000       43_404  0.00000            150608  209.137.198.89:27650  5CXgsEverVvqN2wNVtim5K7xXTFWpq3yrPQajLdAupAp2jsr 
8thtry   miner2770  52    False   1.05528  0.00241  0.78582    0.00301    0.00241    0.00000       46_735  0.00000            150611  209.137.198.90:27700  5H3aczttohdk9sJL3E6AGMUsZAzfdjbACzJVzLxXwugRSA3M 
8thtry   miner2750  205   False   1.07989  0.00235  0.78096    0.00252    0.00235    0.00000       45_532  0.00000            118022  209.137.198.88:27500  5DFUS14rU1kCxfEcGRBnUPw74nurJGpocoii6b9nWUhZMwx3 
                    67                     0.03124  9.82832    0.03764    0.03124    0.00000     ρ605_670  0.00000                                                                                           
Subnet: 28                                                                                                                                                                                                   
COLDKEY  HOTKEY     UID  ACTIVE  STAKE(τ)     RANK     TRUST  CONSENSUS  INCENTIVE  DIVIDENDS  EMISSION(ρ)   VTRUST  VPERMIT  UPDATED  AXON                  HOTKEY_SS58                                     
8thtry   miner2896  181   False   0.81491  0.00482   0.99654    0.00481    0.00482    0.00000       33_191  0.00000             19980  64.247.206.139:28960  5GNeaf34G6xf7msQjd8LVD9dReMMN4ZGd8zBuGVy883k9fbZ
8thtry   miner2891  173   False   0.86547  0.00482   0.99602    0.00481    0.00482    0.00000       33_188  0.00000             20767  64.247.206.236:28910  5D5c4u5JM5GcBYDqm4Ndmr9JiYgPyJKta3p5uwGiefXnQtKG
8thtry   miner2875  179   False   0.81271  0.00482   0.99580    0.00481    0.00482    0.00000       33_191  0.00000             19992  209.137.198.90:28750  5DyZiqeuCu8fQcxDu3eUGNwHb5T1DdiP6x1Qffmq6PPat9fy
8thtry   miner2804  195   False   0.65074  0.00482   0.99600    0.00481    0.00482    0.00000       33_191  0.00000             15648  209.137.198.99:28040  5DRWPHoTeYmeggtnzcwhwAd2i8P1rDrCgH3XanmYbAC142E4
8thtry   miner2812  182   False   0.79144  0.00481   0.99699    0.00481    0.00481    0.00000       33_141  0.00000             19692  64.247.206.91:28120   5EnfTRHCoFo6PcvnPCzsxpoeWr3PbetHfAMJVUeoaSf3P3T5
8thtry   miner2802  194   False   0.67669  0.00481   0.99699    0.00481    0.00481    0.00000       33_137  0.00000             16227  209.137.198.98:28020  5E46m5Vs5ff5xSVyndhknUsrMUrcMPJw6EqSPR7nvvVWjxhN
8thtry   miner2880  184   False   0.80580  0.00481   0.99698    0.00481    0.00481    0.00000       33_137  0.00000             19681  209.137.198.96:28800  5FbwUwdzGcx7qaFmMKv2Zu16fxB7o8xEcVbguhwmCDu616f6
8thtry   miner2805  183   False   0.80678  0.00482   0.99654    0.00481    0.00482    0.00000       33_164  0.00000             19686  209.137.198.95:28050  5H1S4xiftfwrVNENTxq4GyA4cfmouGfAvJgrsbNPQTWt57JX
8thtry   miner2874  174   False   0.79798  0.00482   0.99696    0.00481    0.00482    0.00000       33_159  0.00000             20762  209.137.198.70:28740  5HYrnBxqd1cqYRKtLnRF8sY9GzeDLaiKbHbEtZvnGXZ9kYMe
8thtry   miner2801  192   False   0.67794  0.00482   0.99583    0.00481    0.00482    0.00000       33_191  0.00000             16238  209.137.198.97:28010  5E49WVAfXCH8K7co3FF9z9jjCc5egvDcFtWbdHkHPPVSNufd
8thtry   miner2873  180   False   0.81207  0.00482   0.99623    0.00481    0.00482    0.00000       33_183  0.00000             19985  209.137.198.91:28730  5GbBKto4PWqXgeU8Zi1ZGvpMNGZYJS32LVHs4g21g6wKw86y
8thtry   miner2846  123   False   0.99500  0.00482   0.99631    0.00481    0.00482    0.00000       33_191  0.00000             27239  209.137.198.89:28460  5EFgfwekXJj7r38pmNfeyrGz1jBVzUdu65nTkqaF5TxmPx8y
                    79                     0.05782  11.95720    0.05768    0.05782    0.00000     ρ398_064  0.00000                                                                                          
Subnet: 30                                                                                                                                                                                                   
COLDKEY  HOTKEY     UID  ACTIVE   STAKE(τ)     RANK    TRUST  CONSENSUS  INCENTIVE  DIVIDENDS  EMISSION(ρ)   VTRUST  VPERMIT  UPDATED  AXON  HOTKEY_SS58                                                     
8thtry   miner3003  71    False    0.00239  0.00580  0.96878    0.00574    0.00580    0.00000           17  0.00000            108642  none  5DU2Wvh9GT2cqemUGQoxTvCzBESgGyajuS5UM6R9gqap2qCd                
8thtry   miner3005  73    False    0.00239  0.00580  0.99464    0.00574    0.00580    0.00000           17  0.00000            108629  none  5GTYPkBaqYNis3Nqoguptv8xG44ewVWmZsqFEMSm5kq5pnvJ                
8thtry   miner3006  74    False    0.00239  0.00572  1.00000    0.00574    0.00572    0.00000           17  0.00000            108560  none  5GTbZaC4qUbPtAVtWvnavsgq68pepicYjyEnaZ6ZRhHso7ji                
8thtry   miner3000  50    False    0.00239  0.00580  0.97241    0.00574    0.00580    0.00000           17  0.00000            115674  none  5Ea1rtkrejhYx6Ktcd6cH7y51seXDCZmYKC568NiyMZsoour                
8thtry   miner3007  75    False    0.00239  0.00580  0.97517    0.00574    0.00580    0.00000           17  0.00000            108555  none  5FtES4H34gCaUfNLUt7pePaCkaTfXJ6XCUV5exLyVFLG9HHd                
8thtry   miner3002  52    False    0.00239  0.00577  1.00000    0.00574    0.00577    0.00000           17  0.00000            115666  none  5G1FwF5B63QSsa2N1rxN3DKCPryJ8U4tWhEukM49LeLG8XVw                
8thtry   miner3004  72    False    0.00239  0.00563  1.00000    0.00574    0.00563    0.00000           17  0.00000            108634  none  5DvJEAr6uE4ecaN64K8aWiZzWksFTxUFHn4iBNzFMxAeNMY5                
8thtry   miner3008  76    False    0.00239  0.00572  1.00000    0.00574    0.00572    0.00000           17  0.00000            108532  none  5Giw9JeCofBzpvBXEejVoAgXQS5TdNHEfb2hEZtKZaPmYfRS                
8thtry   miner3001  51    False    0.00239  0.00577  1.00000    0.00574    0.00577    0.00000           17  0.00000            115669  none  5F6uWQZUpLvsoTjgtuYwGAttGyE5Mu8RD9fWKXxifd3vGpJL                
88       88         88           τ37.34133  0.05180  8.91101    0.05164    0.05180    0.00000         ρ153  0.00000                                                                                          
                                                                                       Wallet balance: τ149.620310135                                                                                                      
"""

        lines = output.strip().split("\n")

        subnet = 0

        for line in lines:
            parts = re.split(r"\s+", line.strip())

            if len(parts) > 2:
                if "K" in parts:
                    parts.remove("K")

                if "M" in parts:
                    parts.remove("M")

                if "T" in parts:
                    parts.remove("T")

            print(f"{parts=}")

            # subnet section - get the subnet number
            if parts[0] == "Subnet:":
                subnet = parts[1]

            # miner line
            if parts[0] == "8thtry":
                miner = {
                    "SUBNET": int(subnet),
                    "HOTKEY": parts[1],
                    "UID": int(parts[2]),
                    "ACTIVE": parts[3],
                    "STAKE": float(parts[4]),
                    "RANK": float(parts[5]),
                    "TRUST": float(parts[6]),
                    "CONSENSUS": float(parts[7]),
                    "INCENTIVE": float(parts[8]),
                    "DIVIDENDS": float(parts[9]),
                    "EMISSION": float(parts[10]),
                    "VTRUST": float(parts[11]),
                }

                # if this is a validator
                if len(parts) == 16:
                    miner["VPMERMIT"] = True
                    miner["UPDATED"] = int(parts[13])
                    miner["AXON"] = parts[14]
                    miner["HOTKEY_SS58"] = parts[15]
                else:
                    miner["VPMERMIT"] = False
                    miner["UPDATED"] = int(parts[12])
                    miner["AXON"] = parts[13]
                    miner["HOTKEY_SS58"] = parts[14]

                wallet["miners"].append(miner)

                print(f"{miner=}")

            # final stake line
            if len(parts) == 11:
                print(f"stake line {parts=}")
                wallet["staked_tao"] = float(
                    parts[3][1:]
                )  # remove the first character from the tao

            if parts[0] == "Wallet" and parts[1] == "balance:":
                print(f"balance line {parts=}")
                wallet["wallet_balance"] = float(
                    parts[2][1:]
                )  # remove the first character from the tao

        print(f"{json.dumps(wallet)}")
        return wallet

    # Function to safely convert string to float
    @staticmethod
    def safe_float(s):
        try:
            return float(s)
        except ValueError:
            return None

    @staticmethod
    def unstake_tokens(wallet_hotkey: str) -> bool:
        command = unstake_token_command.substitute(wallet_hotkey=wallet_hotkey)

        try:
            print(f"running {command=}")
            # Start the process
            child = pexpect.spawn(command)

            # Enable logging to standarad output
            child.logfile_read = sys.stdout.buffer

            # Expect balance and cost information
            child.expect("Do you want to unstake from the following keys to .*")
            # print("\nMatched prompt -unstake", child.match.group().decode())
            child.expect(r"(.*)", timeout=120)
            # child.expect("- miner741:5DV5AmHvtruMKirBaTU15625zLnjWxWyjbZ2vaRecqmnYb6f: ")
            # print("\nMatched prompt -miner:", child.match.group().decode())
            # child.expect(r"(^\d+\.\d+e-\d+ .*$)")
            child.expect(r"(.*)")
            # print("\nMatched prompt digits:", child.match.group().decode())
            child.expect(r"(.*)", timeout=120)
            # print("\nMatched prompt [y/n]:", child.match.group().decode(), "sending y")
            child.sendline("y")

            # Expecting password prompt
            child.expect(r"Enter password to unlock key:", timeout=120)
            # print("\nMatched prompt:", child.match.group().decode(), "sending password")
            child.sendline(WALLET_PASSWORD)  # Sending password

            # Expect confirmation:
            child.expect("(Do you want to unstake:)")
            # print("\nMatched prompt:", child.match.group().decode())
            child.sendline("y")

            # Wait for the command to finish and print the output
            child.expect(pexpect.EOF)
            print(child.before.decode())

        except Exception as e:
            print(f"Error unstaking tokens: {e}")
            return False

        time.sleep(
            10
        )  # if we make requests too fast we get a "TxRateLimitExceeded" - need to look for that string and retry

        return True

    @staticmethod
    def generate_html(data, staked_tao, wallet_balance):
        html = "<html>\n"
        html += """
        <head>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-T3c6CoIi6uLrA9TneNEoa7RxnatzjcDSCmG1MXxSR1GAsXEV/Dwwykc2MPK8M2HN" crossorigin="anonymous">
        <style>
        </style>
        </head>
        """
        html += "<body>\n"
        html += """<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js" integrity="sha384-C6RzsynM9kWDrMNeT87bh95OGNyZPhcTNXj1NW7RuBCsyN/o0jlpcV8Qyq46cDfL" crossorigin="anonymous"></script>"""
        subnet = None
        first_table = True
        html += "<table table-striped table-hover>\n"

        # # Create table headers
        # html += "<tr>\n"
        # for key in data[0].keys():
        #     html += f"<th>{key}</th>\n"
        # html += "</tr>\n"

        # # Create table rows
        # html += "<tr>\n"
        for item in data:
            for key in item:
                if key == "SUBNET" and item[key] != subnet:
                    print(f"new subnet")
                    if not first_table:
                        html += "</tr>"
                        html += "</table>"
                        first_table = False

                    subnet = item[key]
                    html += """<table class="table table-striped table-hover">"""

                    html += "<tr>\n"
                    for hkey in data[0].keys():
                        print(f"{hkey=}")
                        html += f"<th>{hkey}</th>\n"
                    html += "</tr>\n"
                    html += """<tbody class="table-group-divider">"""
                print(f"{item[key]=}")
                html += f"<td>{item[key]}</td>\n"
            html += "</tr>\n"

        html += "</table>\n"

        # End table
        html += "<table>\n"
        html += "<tr>\n"
        html += f"<td>Staked Tao:</td><td>{staked_tao}</td>\n"
        html += f"<td>Wallet Balance:</td><td>{wallet_balance}</td>\n"
        html += "</tr>\n"
        html += "</table>\n"

        html += "</body>\n</html>"

        return html


# get wallet into json
wallet = Utils.get_wallet()

# for each miner, unstake any amount over 1
# # iterate over wallet for each hotkey
# for miner in wallet['miners']:
#     # If the hotkey is a miner unstake
#     if miner['VTRUST']==0.0 and miner['STAKE'] > 1:
#         Utils.unstake_tokens(miner['HOTKEY'])

# Sort the list of dictionaries by the age value
sorted_wallet = sorted(wallet["miners"], key=lambda x: x["SUBNET"])

# Generate HTML
html_content = Utils.generate_html(
    sorted_wallet,
    wallet_balance=wallet["wallet_balance"],
    staked_tao=wallet["staked_tao"],
)

# print(html_content)
# # Write HTML to a file
with open("output.html", "w") as file:
    file.write(html_content)
