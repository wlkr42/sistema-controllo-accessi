#include "LoadCrt288lib.h"

//-------------------------------------------------------------------------------------------
void get_int_input(char* szshow, int *ch)
{	
	printf("%s\t", szshow);
	while(scanf("%d",ch) == 0)
		while(getchar() == '\n');
}

void get_str_input(char* szshow, char *ch)
{
	printf("%s\n", szshow);
	while(scanf("%s",ch) == 0)
		while(getchar() == '\n');
}

int menu();
int test();

int main()
{
	char szErrInfo[256] = {0};
	if(!LoadMyLib("/usr/lib/crt_288x_ur.so", szErrInfo))
	{
		fprintf(stderr,"LoadMyLibrary:%s\n\n",szErrInfo);
		while(getchar() == '\n');
		exit(0);
	}
	
	menu();
	test();
	return 0;
}

int menu()
{
	
	printf("\n==========Welcome to using crt_603_vx_test==========\n");
	printf("\t0:  quit.\n");
	printf("\t1:  Show menu .\n");
	printf("\t2:  Turn on the device .\n");
	printf("\t3:  Initialize and unlock .\n");
	printf("\t4:  Check status .\n");
	printf("\t5:  Lock card status .\n");
	printf("\t6:  Lock card .\n");
	printf("\t7:  Indicator operation .\n");
	printf("\t8:  Read all tracks .\n");
	printf("\t9:  Clear track information .\n");
	printf("\t10: Test contact IC card .\n");
	printf("\t11: Test contactless IC card .\n");
}


int test()
{
	int iRet = 0;
	int ich;
	while(1)
	{
		printf("Please select a test option : ");

		//检查输入是否出错，出错继续输入
		while(scanf("%d",&ich) == 0)
			while(getchar() == '\n');
			

		switch(ich)
		{
			case 0:
			{
				g_crt288_drv.CRT288x_CloseConnection();
		   		UnLoadMyLib();
		    		printf("Byebye.\n\n");
		    		exit(0);
			}
			break;
			case 1:
			{
				 menu();
			}
			break;
			case 2:
			{	
				int iOpenType = 0;
				int iComPort = 1;
				int iBaudRate = 19200;
				get_int_input("Please enter the open type, 0 to open in USB mode, 1 to open in COM port mode ", &iOpenType);
				if(iOpenType == 0)
				{
					iRet = g_crt288_drv.CRT288x_OpenConnection(0, iComPort, iBaudRate);
				}
				else
				{
					get_int_input("Please enter the port number, for example, enter 1 for ttys1 :", &iComPort);
					get_int_input("Please enter the baud rate, such as 9600, 19200, 38400, 115200: ", &iBaudRate);
					iRet = g_crt288_drv.CRT288x_OpenConnection(1, iComPort, iBaudRate);
				}
				
				if(iRet != 0 ){
					fprintf(stderr,"CRT288x_OpenConnection Error iRet:%d\n\n", iRet);
				}
				else{
					printf("CRT288x_OpenConnection success! \n\n");
				}
			}
			break;
			case 3:
			{	
				int iType = 1; //解锁
				iRet = g_crt288_drv.CRT288x_InitDev(iType);
				if(iRet != 0 ){
					fprintf(stderr,"CRT288x_InitDev Error iRet:%d\n\n", iRet);
				}
				else{
					printf("CRT288x_InitDev success! \n\n");
				}
			}
			break;
			case 4:
			{	
				iRet = g_crt288_drv.CRT288x_GetCardStatus();
				switch(iRet)
				{
					case 1:
						printf("No card\n");
					    break;
					case 2:
						printf("card not readey\n");
					    break;
					case 3:
						printf("have card \n");
					    break;
					default:
						printf("error \n");
					    break;	
				}
			}
			break;
			case 5:
			{
				iRet = g_crt288_drv.CRT288x_GetLockStatus();
				switch(iRet)
				{
					case 1:
						printf("Not Locked\n");
					    break;
					case 2:
						printf("Locked\n");
					    break;
					default:
						printf("error \n");
					    break;	
				}
			}
			case 6:
			{
				int iLock = 2; //锁卡
				iRet = g_crt288_drv.CRT288x_LockedProcess(iLock);
				if(iRet != 0){
					fprintf(stderr,"CRT288x_LockedProcess Error iRet:%d\n\n", iRet);
				}
				else{
					printf("CRT288x_LockedProcess success! \n\n");
				}
				
			}
			break;
			case 7:
			{
				int iLightType = 2; //所有灯
				int iFlag = 1;   //亮
				iRet = g_crt288_drv.CRT288x_LEDProcess(iLightType, iFlag);
				if(iRet != 0){
					fprintf(stderr,"CRT288x_LEDProcess Error iRet:%d\n\n", iRet);
				}
				else{
					printf("CRT288x_LEDProcess success! \n\n");
				}
			}
			break;
			case 8:
			{
				char szTrack1Data[256] = {0};
				char szTrack2Data[256] = {0};
				char szTrack3Data[256] = {0};
				iRet = g_crt288_drv.CRT288x_ReadAllTracks(szTrack1Data, szTrack2Data, szTrack3Data);
				if(iRet != 0){
					fprintf(stderr,"CRT288x_ReadAllTracks Error iRet:%d\n\n", iRet);
				}
				else{
					printf("CRT288x_ReadAllTracks success! \n\n");
					printf("\tTrack1:%s\n\tTrack2:%s\n\tTrack3:%s \n\n", szTrack1Data, szTrack2Data, szTrack3Data);
				}
			}
			break;
			case 9:
			{
				iRet = g_crt288_drv.CRT288x_ClearTrackData();
				if(iRet != 0){
					fprintf(stderr,"CRT288x_ClearTrackData Error iRet:%d\n\n", iRet);
				}
				else{
					printf("CRT288x_ClearTrackData success! \n\n");
				}
			}
			break;
			case 10:
			{
				int iICType = 0;
				iICType = g_crt288_drv.CRT288x_GetICType();
				switch(iICType)
				{
					case 0:
						printf("Unknow IC Card\n");
						break;
					case 10:
						printf("T=0 CPU Card\n");
						break;
					case 11:
						printf("T=1 CPU Card\n");
						break;
					case 20:
						printf("SL4442 Card\n");
						break;
					case 21:
						printf("SL4428 Card\n");
						break;
					case 30:
						printf("AT24C01 Card\n");
						break;
					case 31:
						printf("AT24C02 Card\n");
						break;
					case 32:
						printf("AT24C04 Card\n");
						break;
					case 33:
						printf("AT24C08 Card\n");
						break;		
					case 34:
						printf("AT24C16 Card\n");
						break;
					case 35:
						printf("AT24C32 Card\n");
						break;
					case 36:
						printf("AT24C64 Card\n");
						break;
					case 37:
						printf("AT24C128 Card\n");
						break;		
					case 38:
						printf("AT24C256 Card\n");
						break;		
					default:
						printf("error");
						break;
				}
				WORD wChipPower = 0x02; //冷复位
				BYTE byAtr[56] = {0};
				int iAtr = 0;
				iRet = g_crt288_drv.CRT288x_ChipPower(iICType, wChipPower, byAtr, &iAtr);
				if(iRet != 0){
					fprintf(stderr,"CRT288x_ChipPower Error iRet:%d\n\n", iRet);
				}
				else{

					printf("CRT288x_ChipPower success! \n");
					int i;
					printf("ATR:");
					for(i=0;i<iAtr;i++)
						printf("%02x ", byAtr[i]);
					printf("\n");
					
					WORD wChipProtocol = 0;  //自动选择
					char sSendData[1024] = {0};
					int iSendLen = strlen(sSendData);
					BYTE byRecvData[1024] = {0};
					int iRecvLen =0;
					
					if(iICType == 10 || iICType == 11) //CPU卡
					{
// 						WORD wChipProtocol = 0;  //自动选择
// 						char sSendData[] = "80AE80006B46554C4C2046554E4354494F4E414C4761739001010010D20122010123456789303130323033303430353036303730383039304130424761739001010010010000000000000000000000000000009507012012310840FFC0008C0201084000000000000000005F03000057";
// 						int iSendLen = strlen(sSendData);
// 						BYTE byRecvData[1024] = {0};
// 						int iRecvLen =0;
					  
						wChipProtocol = 0;  //自动选择
						
						strcpy(sSendData,"00A4040007A0000000031010");
						iSendLen = strlen(sSendData);
						memset(byRecvData,0,1024);
						iRecvLen = 0;					  
						
						iRet = g_crt288_drv.CRT288x_ChipIO(wChipProtocol, iSendLen, (BYTE*)sSendData, &iRecvLen, byRecvData);
						
						if(iRet != 0)
						{
							fprintf(stderr,"CRT288x_ChipIO Error iRet:%d\n\n", iRet);
						}
						else
						{
							printf("CRT288x_ChipIO success! [%s] \n",sSendData);
							printf("Recv:");
							
							for(i=0;i<iRecvLen;i++)
							  printf("%02x ", byRecvData[i]);
							printf("\n");
						}
					}
					sleep(1);
					if(iICType == 10 || iICType == 11) //CPU卡
					{
// 						WORD wChipProtocol = 0;  //自动选择
// 						char sSendData[] = "0084000008";
// 						int iSendLen = strlen(sSendData);
// 						BYTE byRecvData[1024] = {0};
// 						int iRecvLen =0;
					  
					  	wChipProtocol = 0;  //自动选择
						
						strcpy(sSendData,"00B2010C00");
						iSendLen = strlen(sSendData);
						memset(byRecvData,0,1024);
						iRecvLen = 0;					  
						
						iRet = g_crt288_drv.CRT288x_ChipIO(wChipProtocol, iSendLen, (BYTE*)sSendData, &iRecvLen, byRecvData);
						
						if(iRet != 0)
						{
							fprintf(stderr,"CRT288x_ChipIO Error iRet:%d\n\n", iRet);
						}
						else
						{
							printf("CRT288x_ChipIO success! [%s] \n",sSendData);
							printf("Recv:");
							
							for(i=0;i<iRecvLen;i++)
							  printf("%02x ", byRecvData[i]);
							printf("\n");
						}
					}
					sleep(1);
					if(iICType == 10 || iICType == 11) //CPU卡
					{
					  	wChipProtocol = 0;  //自动选择
						
						strcpy(sSendData,"00B2011400");
						iSendLen = strlen(sSendData);
						memset(byRecvData,0,1024);
						iRecvLen = 0;					  
						
						iRet = g_crt288_drv.CRT288x_ChipIO(wChipProtocol, iSendLen, (BYTE*)sSendData, &iRecvLen, byRecvData);
						
						if(iRet != 0)
						{
							fprintf(stderr,"CRT288x_ChipIO Error iRet:%d\n\n", iRet);
						}
						else
						{
							printf("CRT288x_ChipIO success! [%s] \n",sSendData);
							printf("Recv:");
							
							for(i=0;i<iRecvLen;i++)
							  printf("%02x ", byRecvData[i]);
							printf("\n");
						}
					}
					/* sleep(1);
					if(iICType == 10 || iICType == 11) //CPU卡
					{
					  	wChipProtocol = 0;  //自动选择
						
						strcpy(sSendData,"00A4040007A0000000031010");
						iSendLen = strlen(sSendData);
						memset(byRecvData,0,1024);
						iRecvLen = 0;					  
						
						iRet = g_crt288_drv.CRT288x_ChipIO(wChipProtocol, iSendLen, (BYTE*)sSendData, &iRecvLen, byRecvData);
						
						if(iRet != 0)
						{
							fprintf(stderr,"CRT288x_ChipIO Error iRet:%d\n\n", iRet);
						}
						else
						{
							printf("CRT288x_ChipIO success! [%s] \n",sSendData);
							printf("Recv:");
							
							for(i=0;i<iRecvLen;i++)
							  printf("%02x ", byRecvData[i]);
							printf("\n");
						}
					}
					sleep(1);
					if(iICType == 10 || iICType == 11) //CPU卡
					{
					  	wChipProtocol = 0;  //自动选择
						
						strcpy(sSendData,"80A8000013831108406040208E80F053FF00003AB1009614");
						iSendLen = strlen(sSendData);
						memset(byRecvData,0,1024);
						iRecvLen = 0;					  
						
						iRet = g_crt288_drv.CRT288x_ChipIO(wChipProtocol, iSendLen, (BYTE*)sSendData, &iRecvLen, byRecvData);
						
						if(iRet != 0)
						{
							fprintf(stderr,"CRT288x_ChipIO Error iRet:%d\n\n", iRet);
						}
						else
						{
							printf("CRT288x_ChipIO success! [%s] \n",sSendData);
							printf("Recv:");
							
							for(i=0;i<iRecvLen;i++)
							  printf("%02x ", byRecvData[i]);
							printf("\n");
						}
					}
					sleep(1);
					if(iICType == 10 || iICType == 11) //CPU卡
					{
					  	wChipProtocol = 0;  //自动选择
						
						strcpy(sSendData,"00B2010C00");
						iSendLen = strlen(sSendData);
						memset(byRecvData,0,1024);
						iRecvLen = 0;					  
						
						iRet = g_crt288_drv.CRT288x_ChipIO(wChipProtocol, iSendLen, (BYTE*)sSendData, &iRecvLen, byRecvData);
						
						if(iRet != 0)
						{
							fprintf(stderr,"CRT288x_ChipIO Error iRet:%d\n\n", iRet);
						}
						else
						{
							printf("CRT288x_ChipIO success! [%s] \n",sSendData);
							printf("Recv:");
							
							for(i=0;i<iRecvLen;i++)
							  printf("%02x ", byRecvData[i]);
							printf("\n");
						}
					}
					sleep(1);
					if(iICType == 10 || iICType == 11) //CPU卡
					{
					  	wChipProtocol = 0;  //自动选择
						
						strcpy(sSendData,"00B2011400");
						iSendLen = strlen(sSendData);
						memset(byRecvData,0,1024);
						iRecvLen = 0;					  
						
						iRet = g_crt288_drv.CRT288x_ChipIO(wChipProtocol, iSendLen, (BYTE*)sSendData, &iRecvLen, byRecvData);
						
						if(iRet != 0)
						{
							fprintf(stderr,"CRT288x_ChipIO Error iRet:%d\n\n", iRet);
						}
						else
						{
							printf("CRT288x_ChipIO success! [%s] \n",sSendData);
							printf("Recv:");
							
							for(i=0;i<iRecvLen;i++)
							  printf("%02x ", byRecvData[i]);
							printf("\n");
						}
					}
					sleep(1);
					if(iICType == 10 || iICType == 11) //CPU卡
					{
					  	wChipProtocol = 0;  //自动选择
						
						strcpy(sSendData,"00B2021400");
						iSendLen = strlen(sSendData);
						memset(byRecvData,0,1024);
						iRecvLen = 0;					  
						
						iRet = g_crt288_drv.CRT288x_ChipIO(wChipProtocol, iSendLen, (BYTE*)sSendData, &iRecvLen, byRecvData);
						
						if(iRet != 0)
						{
							fprintf(stderr,"CRT288x_ChipIO Error iRet:%d\n\n", iRet);
						}
						else
						{
							printf("CRT288x_ChipIO success! [%s] \n",sSendData);
							printf("Recv:");
							
							for(i=0;i<iRecvLen;i++)
							  printf("%02x ", byRecvData[i]);
							printf("\n");
						}
					}
					
										if(iICType == 10 || iICType == 11) //CPU卡
					{
					  	wChipProtocol = 0;  //自动选择
						
						strcpy(sSendData,"00B2031400");
						iSendLen = strlen(sSendData);
						memset(byRecvData,0,1024);
						iRecvLen = 0;					  
						
						iRet = g_crt288_drv.CRT288x_ChipIO(wChipProtocol, iSendLen, (BYTE*)sSendData, &iRecvLen, byRecvData);
						
						if(iRet != 0)
						{
							fprintf(stderr,"CRT288x_ChipIO Error iRet:%d\n\n", iRet);
						}
						else
						{
							printf("CRT288x_ChipIO success! [%s] \n",sSendData);
							printf("Recv:");
							
							for(i=0;i<iRecvLen;i++)
							  printf("%02x ", byRecvData[i]);
							printf("\n");
						}
					}
					
										if(iICType == 10 || iICType == 11) //CPU卡
					{
					  	wChipProtocol = 0;  //自动选择
						
						strcpy(sSendData,"00B2011C00");
						iSendLen = strlen(sSendData);
						memset(byRecvData,0,1024);
						iRecvLen = 0;					  
						
						iRet = g_crt288_drv.CRT288x_ChipIO(wChipProtocol, iSendLen, (BYTE*)sSendData, &iRecvLen, byRecvData);
						
						if(iRet != 0)
						{
							fprintf(stderr,"CRT288x_ChipIO Error iRet:%d\n\n", iRet);
						}
						else
						{
							printf("CRT288x_ChipIO success! [%s] \n",sSendData);
							printf("Recv:");
							
							for(i=0;i<iRecvLen;i++)
							  printf("%02x ", byRecvData[i]);
							printf("\n");
						}
					}
					
										if(iICType == 10 || iICType == 11) //CPU卡
					{
					  	wChipProtocol = 0;  //自动选择
						
						strcpy(sSendData,"00B2021C00");
						iSendLen = strlen(sSendData);
						memset(byRecvData,0,1024);
						iRecvLen = 0;					  
						
						iRet = g_crt288_drv.CRT288x_ChipIO(wChipProtocol, iSendLen, (BYTE*)sSendData, &iRecvLen, byRecvData);
						
						if(iRet != 0)
						{
							fprintf(stderr,"CRT288x_ChipIO Error iRet:%d\n\n", iRet);
						}
						else
						{
							printf("CRT288x_ChipIO success! [%s] \n",sSendData);
							printf("Recv:");
							
							for(i=0;i<iRecvLen;i++)
							  printf("%02x ", byRecvData[i]);
							printf("\n");
						}
					}
					
										if(iICType == 10 || iICType == 11) //CPU卡
					{
					  	wChipProtocol = 0;  //自动选择
						
						strcpy(sSendData,"00B2031C00");
						iSendLen = strlen(sSendData);
						memset(byRecvData,0,1024);
						iRecvLen = 0;					  
						
						iRet = g_crt288_drv.CRT288x_ChipIO(wChipProtocol, iSendLen, (BYTE*)sSendData, &iRecvLen, byRecvData);
						
						if(iRet != 0)
						{
							fprintf(stderr,"CRT288x_ChipIO Error iRet:%d\n\n", iRet);
						}
						else
						{
							printf("CRT288x_ChipIO success! [%s] \n",sSendData);
							printf("Recv:");
							
							for(i=0;i<iRecvLen;i++)
							  printf("%02x ", byRecvData[i]);
							printf("\n");
						}
					}
					
										if(iICType == 10 || iICType == 11) //CPU卡
					{
					  	wChipProtocol = 0;  //自动选择
						
						strcpy(sSendData,"80AE80006B46554C4C2046554E4354494F4E414C4761739001010010D20122010123456789303130323033303430353036303730383039304130424761739001010010010000000000000000000000000000009507012012310840FFC0008C0201084000000000000000005F03000057");
						iSendLen = strlen(sSendData);
						memset(byRecvData,0,1024);
						iRecvLen = 0;					  
						
						iRet = g_crt288_drv.CRT288x_ChipIO(wChipProtocol, iSendLen, (BYTE*)sSendData, &iRecvLen, byRecvData);
						
						if(iRet != 0)
						{
							fprintf(stderr,"CRT288x_ChipIO Error iRet:%d\n\n", iRet);
						}
						else
						{
							printf("CRT288x_ChipIO success! [%s] \n",sSendData);
							printf("Recv:");
							
							for(i=0;i<iRecvLen;i++)
							  printf("%02x ", byRecvData[i]);
							printf("\n");
						}
					}
					
										if(iICType == 10 || iICType == 11) //CPU卡
					{
					  	wChipProtocol = 0;  //自动选择
						
						strcpy(sSendData,"80AE400009CF29433980C0800080");
						iSendLen = strlen(sSendData);
						memset(byRecvData,0,1024);
						iRecvLen = 0;					  
						
						iRet = g_crt288_drv.CRT288x_ChipIO(wChipProtocol, iSendLen, (BYTE*)sSendData, &iRecvLen, byRecvData);
						
						if(iRet != 0)
						{
							fprintf(stderr,"CRT288x_ChipIO Error iRet:%d\n\n", iRet);
						}
						else
						{
							printf("CRT288x_ChipIO success! [%s] \n",sSendData);
							printf("Recv:");
							
							for(i=0;i<iRecvLen;i++)
							  printf("%02x ", byRecvData[i]);
							printf("\n");
						}
					} */
				}
				
			}
			break;
			case 11:
			{
				int iRFType = 0;
				iRFType = g_crt288_drv.CRT288x_GetRFType();
				switch(iRFType)
				{
					case 0:
						printf("Unknow RF Card\n");
						break;
					case 110:
						printf("S50 Card\n");
						break;
					case 111:
						printf("S70 Card\n");
						break;
					case 112:
						printf("UL Card\n");
						break;
					case 120:
						printf("TypeA CPU Card\n");
						break;
					case 130:
						printf("TypeB CPU Card\n");
						break;	
					default:
						printf("error");
						break;
				}
				WORD wChipPower = 0x02; //冷复位
				BYTE byAtr[56] = {0};
				int iAtr = 0;
				iRet = g_crt288_drv.CRT288x_ChipPower(iRFType, wChipPower, byAtr, &iAtr);
				if(iRet != 0){
					fprintf(stderr,"CRT288x_ChipPower Error iRet:%d\n\n", iRet);
				}
				else{
					printf("CRT288x_ChipPower success! \n");
					int i;
					printf("ATR:");
					for(i=0;i<iAtr;i++)
						printf("%02x ", byAtr[i]);
					printf("\n");
					
					if(iRFType == 120 || iRFType == 130) //CPU卡
					{
						WORD wChipProtocol = 0;  //自动选择
						char sSendData[] = "0084000008";
						int iSendLen = strlen(sSendData);
						BYTE byRecvData[1024] = {0};
						int iRecvLen =0;
						
						iRet = g_crt288_drv.CRT288x_ChipIO(wChipProtocol, iSendLen, (BYTE*)sSendData, &iRecvLen, byRecvData);
						if(iRet != 0){
							fprintf(stderr,"CRT288x_ChipIO Error iRet:%d\n\n", iRet);
						}
						else{
							printf("CRT288x_ChipIO success! \n");
							printf("Recv:");
							for(i=0;i<iRecvLen;i++)
							printf("%02x ", byRecvData[i]);
							printf("\n");
						}
					}
				}
				
			}
			break;
			default:
			printf("you chosen is error.\n\n");
			break;
			
		}
	}
}
