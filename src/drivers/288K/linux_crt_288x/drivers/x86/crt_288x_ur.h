#ifndef __CRT_288K_UR__
#define __CRT_288K_UR__
#include <stdbool.h>

#define BYTE unsigned char
#define WORD unsigned short 
#define DWORD unsigned int

//ͨѶЭ��
#define ENQ  0x05
#define ACK  0x06
#define NAK  0x15
#define EOT  0x04
#define CAN  0x18
#define STX  0xF2
#define ETX  0x03
#define US   0x1F

//������
#define CRT_ERRCOUNT                 -200
#define CRT_ERR_CMD                  (CRT_ERRCOUNT-1) //�����ִ���
#define CRT_ERR_CMDPARAM             (CRT_ERRCOUNT-2) //�����������
#define CRT_ERR_CMDDENIAL            (CRT_ERRCOUNT-3) //����ܱ�ִ��
#define CRT_ERR_DEVNOTSUP            (CRT_ERRCOUNT-4) //Ӳ����֧��
#define CRT_ERR_CMDDATA              (CRT_ERRCOUNT-5) //�������ݴ���
#define CRT_ERR_LOCKCARD             (CRT_ERRCOUNT-11) //����������ʧ��
#define CRT_ERR_EEPROM               (CRT_ERRCOUNT-15) //EEPROM error
#define CRT_ERR_TRACKCHECK           (CRT_ERRCOUNT-20) //���ſ���У���
#define CRT_ERR_READTRACK            (CRT_ERRCOUNT-21) //���ſ���
#define CRT_ERR_POWERDOWN            (CRT_ERRCOUNT-30) //�������磨Power down��
#define CRT_ERR_ICPROCESS            (CRT_ERRCOUNT-41) //IC��ģ�����ʧ��
#define CRT_ERR_ICPOWERSHORT         (CRT_ERRCOUNT-60) //IC����Դ��·
#define CRT_ERR_ICACTIVATIONFAIL     (CRT_ERRCOUNT-61) //IC������ʧ��
#define CRT_ERR_ICDENIAL             (CRT_ERRCOUNT-62) //IC����֧�ֵ�ǰ����
#define CRT_ERR_ICNOTRESPOND         (CRT_ERRCOUNT-63) //IC��ͨѶ����
#define CRT_ERR_ICNOTRESPOND_OTHER   (CRT_ERRCOUNT-64) //IC��ͨѶ����(����)
#define CRT_ERR_ICNOTACTIVATION      (CRT_ERRCOUNT-65) //IC��δ����
#define CRT_ERR_ICNOTSUP             (CRT_ERRCOUNT-66) //������֧������IC��
#define CRT_ERR_ICEMV                (CRT_ERRCOUNT-66) //��֧��EMVģʽ
#define CRT_ERR_COMMTIMEOUT	         (CRT_ERRCOUNT-80) //ͨѶʧ�ܳ�ʱ
#define CRT_ERR_CANCEL	             (CRT_ERRCOUNT-84) //����ȡ��
#define CRT_ERR_PWDPROCESS	         (CRT_ERRCOUNT-90) //У���������ʧ��
#define CRT_ERR_PWDCHECK	         (CRT_ERRCOUNT-91) //����У��ʧ��
#define CRT_ERR_PWDSCRAP	         (CRT_ERRCOUNT-92) //����У��ʧ�ܣ�������
#define CRT_ERR_PWDADDROVERFLOW	     (CRT_ERRCOUNT-93) //������ַ���
#define CRT_ERR_PWDLENOVERFLOW	     (CRT_ERRCOUNT-94) //�����������
#define CRT_ERR_PWDPMERR	         (CRT_ERRCOUNT-95) //PM ����
#define CRT_ERR_PWDCMERR	         (CRT_ERRCOUNT-96) //CM ����
#define CRT_ERR_UNKNOWN              (CRT_ERRCOUNT-99) //δ֪����

//���豸
#define CRT_OPEN_TYPEUSB             0 //USB�ڷ�ʽ���豸
#define CRT_OPEN_TYPERS232           1 //RS232�ڷ�ʽ���豸

//��ʼ��
#define CRT_INIT_NOTUNLOCK          0 //��ʼ���޶���
#define CRT_INIT_UNLOCK             1 //��ʼ������


//��״̬
#define CRT_CARDST_NOCARD             1 //�޿�
#define CRT_CARDST_INDOOR             2 //����
#define CRT_CARDST_INSIDE             3 //����
#define CRT_CARDST_UNKNOW             9 //�豸�����ߣ���״̬δ֪

//����״̬
#define CRT_LOCKCARD_NOTLOCK            1 //δ����
#define CRT_LOCKCARD_LOCKED             2 //������
#define CRT_LOCKCARD_UNKNOW             9 //�豸������,����״̬δ֪

//����������
#define CRT_RDACTION_NOACTION           0 //�޶���
#define CRT_RDACTION_UNLOCK             1 //����
#define CRT_RDACTION_LOCKED             2 //����
#define CRT_RDACTION_AUTOLOCKED         3 //�п��Զ�����
#define CRT_RDACTION_NOTAUTOLOCK        4 //�п����Զ�����

//����ָʾ��
#define  CRT_LED_RED                    0 //������ɫָʾ��
#define  CRT_LED_BLUE                   1 //������ɫָʾ��
#define  CRT_LED_ALL                    2 //��������ָʾ��

//�ƿ���
#define  CRT_LED_OFF                    0 //ָʾ�ƹر�
#define  CRT_LED_ON                     1 //ָʾ�ƴ�
#define  CRT_LED_FLASHING               2 //ָʾ����˸

//��������ȡ����
#define CRT_SETMAGTYPE_READASCII        0x00000000 //��ASCII����ŵ�����
#define CRT_SETMAGTYPE_READHEX          0x00000001 //�Զ����Ʒ�ʽ���ŵ�����
#define CRT_SETMAGTYPE_AUTOUPLOAD       0x00000000 //�����ϴ��ŵ�����
#define CRT_SETMAGTYPE_NOTUPLOAD        0x00000010 //��ֹ�����ϴ��ŵ�����
#define CRT_SETMAGTYPE_EFFINSERT        0x00000000 //������ŵ�������Ч
#define CRT_SETMAGTYPE_EFFUPPLUG        0x00000100 //�γ����ŵ�������Ч

//���ŵ���
#define CRT_ReadTracks_Track1           1 //�ŵ�1����
#define CRT_ReadTracks_Track2           2 //�ŵ�2����
#define CRT_ReadTracks_Track3           3 //�ŵ�3����

/** 
 * @fn		CRT288x_OpenConnection() 
 * @detail	���豸
 * @see		...
 * @param	[in]iOpenMode--��ģʽ:0 USB����ģʽ�� 1 RS232����ģʽ
 * @param	[in]iComPort--����COM��(USBģʽ�£����账��)
 * @param	[in]lBaudRate--���ò�����(Ĭ�� 9600)
 * @return	���,0�ɹ�����0����.
 * @exception ...
 * @example USB���ӣ�int iRet = CRT288x_OpenConnection(0); 
            COM3,������9600 ���ӣ�int iRet = CRT288x_OpenConnection(1, 3, 9600);
 * @author	luowei
 * @date	2016/01/06
 */
int CRT288x_OpenConnection(int iOpenMode, int iComPort, long lBaudRate);



/** 
 * @fn		CRT288x_CloseConnection() 
 * @detail	�ر��豸
 * @see		...
 * @return	���,0�ɹ�����0����
 * @exception ...
 * @example int iRet = CRT288x_CloseConnection(); 
 * @author	luowei
 * @date	2016/01/06
 */
int CRT288x_CloseConnection();



/** 
 * @fn		CRT288x_ExeCommand() 
 * @detail	����ִ������
 * @see		...
 * @param	[in]iSendDataLen:���͵������
 * @param	[in]bySendData:���͵�����
 * @param	[out]iRecvDataLen:���ص������
 * @param	[out]byRecvData:���ص�����
 * @param	[out]byStCode:���ص�ִ��״̬��
 * @return	���,0�ɹ�����0����
 * @exception ...
 *
 * @author	luowei
 * @date	2016/01/06
 */
int  CRT288x_ExeCommand(int iSendDataLen, BYTE bySendData[] , int* iRecvDataLen, BYTE byRecvData[],BYTE byStCode[]);



/** 
 * @fn		CRT288x_InitDev() 
 * @detail	��ʼ���豸
 * @see		...
 * @param	[in]InitMode--��ʼ��ģʽ:0 �޶����� 1 ����
 * @return	���,0�ɹ�����0����
 * @exception ...
 *
 * @author	luowei
 * @date	2016/01/06
 */
int CRT288x_InitDev(int InitMode );


/** 
 * @fn		CRT288x_GetCardStatus() 
 * @detail	��ȡ��Ƭ״̬
 * @see		...
 * @return	��Ƭ״̬: 1 �޿���2 ���ڿ��ڣ� 3 ���ڶ������ڣ� 9 �豸�����ߣ���״̬δ֪��
 * @exception ...
 *
 * @author	luowei
 * @date	2016/01/06
 */
int  CRT288x_GetCardStatus();



/** 
 * @fn		CRT288x_GetLockStatus() 
 * @detail	��ȡ����״̬
 * @see		...
 * @return	��Ƭ״̬: 1 δ������2 �������� 9 �豸�����ߣ�����״̬δ֪��
 * @exception ...
 *
 * @author	luowei
 * @date	2016/01/06
 */
int  CRT288x_GetLockStatus();



/** 
 * @fn		CRT288x_LockedProcess() 
 * @detail	��������
 * @see		...
 * @param	[in]iLockType--������������:0 �޶����� 1 ������ 2 ������ 3 �п��Զ������� 4 �п����Զ�����
 * @return	���,0�ɹ�����0����
 * @exception ...
 *
 * @author	luowei
 * @date	2016/01/06
 */
int  CRT288x_LockedProcess(int iLockType);



/** 
 * @fn		CRT288x_LEDProcess() 
 * @detail	ָʾ�Ʋ���
 * @see		...
 * @param	[in]iLightType--����ָʾ��:0 ��ɫָʾ�ƣ�1 ��ɫָʾ�ƣ� 2 ����ָʾ��
 * @param	[in]iFlag--ָʾ��״̬:0 ��1 ���� 2 ��˸
 * @return	���,0�ɹ�����0����
 * @exception ...
 *
 * @author	luowei
 * @date	2016/01/06
 */
int  CRT288x_LEDProcess(int iLightType, int iFlag);



/** 
 * @fn		CRT288x_SetLEDFlashTime() 
 * @detail	����ָʾ����˸ʱ��
 * @see		...
 * @param	[in]iOnTime--ָʾ����˸ ��ʱ��: ��0x00-0xFF��*0.25��
 * @param	[in]iOffTime--ָʾ����˸ ��ʱ��: ��0x00-0xFF��*0.25��
 * @return	���,0�ɹ�����0����
 * @exception ...
 *
 * @author	luowei
 * @date	2016/01/06
 */
int  CRT288x_SetLEDFlashTime(int iOnTime, int iOffTime);



/** 
 * @fn		CRT288x_SetReaderMagType() 
 * @detail	���ö��������ſ���ʽ
 * @see		...
 * @param	[in]iReadMode--������ʽ: 0 ASCII��������ݣ� 1 ���������������
 * @param	[in]iDataMode--������Ч��ʽ: 0 �忨������Ч�� 1 �ο�������Ч 
  * @param	[in]bAutoUpload--�Ƿ������ϴ�: TRUE ���������ϴ��� FALSE ��ֹ�����ϴ� 
 * @return	���,0�ɹ�����0����
 * @exception ...
 *
 * @author	luowei
 * @date	2016/01/06
 */
int  CRT288x_SetReaderMagType(int iReadMode, int iDataMode, bool bAutoUpload);



/** 
 * @fn		CRT288x_ReadTrack() 
 * @detail	�����ŵ�����
 * @see		...
 * @param	[in]iTrackNum--�ŵ���: 1 һ�ŵ��� 2 ���ŵ��� 3 ���ŵ�
 * @param	[out]szTrackData--���شŵ����� 
 * @return	���,0�ɹ�����0����
 * @exception ...
 *
 * @author	luowei
 * @date	2016/01/06
 */
int  CRT288x_ReadTrack(int iTrackNum, char szTrackData[]);




/** 
 * @fn		CRT288x_ReadAllTracks() 
 * @detail	�����дŵ�����
 * @see		...
 * @param	[out]szTrack1Data--����һ�ŵ�����
 * @param	[out]szTrack2Data--���ض��ŵ�����
 * @param	[out]szTrack3Data--�������ŵ�����
 * @return	���,0�ɹ�����0����
 * @exception ...
 *
 * @author	luowei
 * @date	2016/01/06
 */
int  CRT288x_ReadAllTracks(char szTrack1Data[], char szTrack2Data[], char szTrack3Data[]);



/** 
 * @fn		CRT288x_ClearTrackData() 
 * @detail	����������ŵ�����
 * @see		...
 * @return	���,0�ɹ�����0����
 * @exception ...
 *
 * @author	luowei
 * @date	2016/01/06
 */
int  CRT288x_ClearTrackData();



/** 
 * @fn		CRT288x_GetICType() 
 * @detail	��ȡ(�Ӵ�ʽ)IC������
 * @see		...
 * @return	���,0 δ֪IC�����ͣ���0ʧ�ܣ� 10 T=0 CPU���� 11 T=1 CPU���� 20 SL4442���� 21 SL4428���� 30 AT24C01���� 31 AT24C02���� 32 AT24C04����
                 33 AT24C08���� 34 AT24C16���� 35 AT24C32���� 36 AT24C64���� 37 AT24C128���� 38 AT24C256���� 
 * @exception ...
 *
 * @author	luowei
 * @date	2016/01/06
 */
int  CRT288x_GetICType();



/** 
 * @fn		CRT288x_GetRFType() 
 * @detail	��ȡ(�ǽӴ�ʽ)RF������
 * @see		...
 * @return	���,0 δ֪RF�����ͣ���0ʧ�ܣ� 110 S50���� 111 S70���� 112 UL���� 120 TypeA CPU���� 130 TypeB CPU����
 * @exception ...
 *
 * @author	luowei
 * @date	2016/01/06
 */
int  CRT288x_GetRFType();



/** 
 * @fn		CRT288x_ChipPower() 
 * @detail	IC���ϵ����
 * @see		...
 * @param	[in]iICType--IC������:10 T=0 CPU���� 11 T=1 CPU���� 20 SL4442���� 21 SL4428���� 30 AT24C01���� 31 AT24C02���� 32 AT24C04����
							  33 AT24C08���� 34 AT24C16���� 35 AT24C32���� 36 AT24C64���� 37 AT24C128���� 38 AT24C256��
							  110 S50���� 111 S70���� 112 UL���� 120 TypeA CPU���� 130 TypeB CPU���� 210 SAM ����
 * @param	[in]wChipPower--�ϵ����: 0x02 �临λ�ϵ磬 0x04 �ȸ�λ�ϵ磬 0x08 �µ硣
 * @param	[out]byOutChipData--�临λ����ATR����
 * @param	[out]iOutChipDatalen--�临λ����ATR���ݳ���
 * @return	���,0�ɹ�����0ʧ�ܡ�
 * @exception ...
 *
 * @author	luowei
 * @date	2016/01/06
 */
int  CRT288x_ChipPower(int iICType, WORD wChipPower, BYTE byOutChipData[], int* iOutChipDatalen);




/** 
 * @fn		CRT288x_ChipIO() 
 * @detail	��IC��оƬͨѶ
 * @see		...
 * @param	[in]wChipProtocol--IC��ͨѶЭ��: 0 �������Զ�ѡ��Э�飬1 T0Э�飬 2 T1Э�顣
 * @param	[in]ulInChipDataLength--����APDU���ݳ��ȡ�
 * @param	[in]lpInbChipData--����APDU����
 * @param	[out]ulOutChipDataLength--���ص�APDU���ݳ���
 * @param	[out]lpOutbChipData--���ص�APDU����
 * @return	���,0�ɹ�����0ʧ�ܡ�
 * @exception ...
 *
 * @author	luowei
 * @date	2016/01/06
 */
int  CRT288x_ChipIO(WORD wChipProtocol, int ulInChipDataLength , BYTE lpInbChipData[], int* ulOutChipDataLength , BYTE lpOutbChipData[]);




/** 
 * @fn		CRT288x_GetCardActiveStatus() 
 * @detail	��ѯ��ǰICоƬ�ļ���״̬
 * @see		...
 * @return	���,1 ��Ƭ�Ѽ����ǰCPU ������ʱ��Ƶ��Ϊ3.57 MHZ�� 2 ��Ƭ�Ѽ����ǰCPU ������ʱ��Ƶ��Ϊ7.16 MHZ�� 3 δ��� 9����״̬δ֪����0ʧ�ܡ�
 * @exception ...
 *
 * @author	luowei
 * @date	2016/01/06
 */
int  CRT288x_GetCardActiveStatus();




/** 
 * @fn		CRT288x_SAMSlotChange() 
 * @detail	SAM���л�����
 * @see		...
 * @param	[in]iSamNum--���л��Ŀ���(1-10) 1 SAM1������ 2 SAM2������ 3 SAM3������ 4 SAM4����
 * @return	���,0�ɹ�����0ʧ�ܡ�
 * @exception ...
 *
 * @author	luowei
 * @date	2016/01/06
 */
int  CRT288x_SAMSlotChange(int iSamNum);




/** 
 * @fn		CRT288x_SetVcc() 
 * @detail	�����ϵ�Vcc����
 * @see		...
 * @param	[in]iVcc--Vcc���� 1 5V��Դ��EMV��ʽ��� 2 5V��Դ��ISO7816��ʽ��� 3 3V��Դ��ISO7816��ʽ����
 * @return	���,0�ɹ�����0ʧ�ܡ�
 * @exception ...
 *
 * @author	luowei
 * @date	2016/01/06
 */
int  CRT288x_SetVcc(int iVcc);




/** 
 * @fn		CRT288x_SL4442CheckPasswd() 
 * @detail	SL4442����У������
 * @see		...
 * @param	[in]iMode--����ģʽ 1 У�����룬 2 �޸�����
 * @param	[in]uDataLength--����ĳ���
 * @param	[in]lpData--У�������(Ĭ�����룺FFFFFF)
 * @return	���,0�ɹ�����0ʧ�ܡ�
 * @exception ע�⣺�û�Ҫ��дSLE4442�����ݱ���֪���������룬������������ֵ���2 ��С��2 ��ֱֵ����λ���㣬���������ֵΪ
 * ��ʱ����Ƭ�������ϡ�
 *
 * @author	luowei
 * @date	2016/01/06
 */
int  CRT288x_SL4442CheckPasswd(int iMode, int uDataLength, BYTE lpData[]);






/** 
 * @fn		CRT288x_SL4442Process() 
 * @detail	SL4442���Ķ�д����
 * @see		...
 * @param	[in]iMode--����ģʽ   1 ���� 2 д
 * @param	[in]iRegion--��������   1 ���洢���� 2 ����λ���� 3 ��ȫ��
 * @param	[in]wStartAddr--��ʼλ��(0x00-0xFF)
 * @param	[in][out]uDataLength--���������ݳ���(���洢����0-128�� ����λ����0-4�� ��ȫ����0-4)
 * @param	[in][out]lpData--����������(ģʽΪд�������롣 ģʽΪ���� �����)
 * @return	���,0�ɹ�����0ʧ�ܡ�
 * @exception ...
 *
 * @author	luowei
 * @date	2016/01/06
 */
int  CRT288x_SL4442Process(int iMode, int iRegion ,WORD wStartAddr, int* uDataLength, BYTE lpData[]);






/** 
 * @fn		CRT288x_SL4428CheckPasswd() 
 * @detail	SL4428����У������
 * @see		...
 * @param	[in]iMode--����ģʽ 1 У�����룬 2 �޸�����
 * @param	[in]uDataLength--����ĳ���
 * @param	[in]lpData--У�������(Ĭ�����룺FFFF)
 * @return	���,0�ɹ�����0ʧ�ܡ�
 * @exception ע�⣺�û�Ҫ��дSLE4428�����ݱ���֪���������룬������������ֵ���7 ��С��7 ��ֱֵ����λ���㣬���������ֵΪ
 * ��ʱ����Ƭ�������ϡ�
 *
 * @author	luowei
 * @date	2016/01/06
 */
int  CRT288x_SL4428CheckPasswd(int iMode, int uDataLength, BYTE lpData[]);





/** 
 * @fn		CRT288x_SL4428Process() 
 * @detail	SL4428���Ķ�д����
 * @see		...
 * @param	[in]iMode--����ģʽ   1 ���� 2 д
 * @param	[in]iRegion--��������   1 ���洢���� 2 ����λ��
 * @param	[in]wStartAddr--��ʼλ��(0x00-0x01FF)
 * @param	[in][out]uDataLength--���������ݳ���(���洢����0-256�� ����λ����0-128)
 * @param	[in][out]lpData--����������(ģʽΪд�������롣 ģʽΪ���� �����)
 * @return	���,0�ɹ�����0ʧ�ܡ�
 * @exception ...
 *
 * @author	luowei
 * @date	2016/01/06
 */
int  CRT288x_SL4428Process(int iMode, int iRegion ,WORD wStartAddr, int* uDataLength, BYTE lpData[]);





/** 
 * @fn		CRT288x_24CxProcess() 
 * @detail	24Cx���Ķ�д����
 * @see		...
 * @param	[in]iMode--����ģʽ   1 ���� 2 д
 * @param	[in]wStartAddr--��ʼλ��(24C01: 0x00-0x07F, 24C02: 0x00-0xFF, 24C04: 0x00-0x01FF, 24C08: 0x00-0x03FF, 24C16: 0x00-0x07FF,
                                 24C32: 0x00-0x0FFF, 24C64: 0x00-0x1FFF, 24C128: 0x00-0x3FFF, 24C256: 0x00-0x7FFF)
 * @param	[in][out]uDataLength--���������ݳ���
 * @param	[in][out]lpData--����������(ģʽΪд�������롣 ģʽΪ���� �����)
 * @return	���,0�ɹ�����0ʧ�ܡ�
 * @exception ...
 *
 * @author	luowei
 * @date	2016/01/06
 */
int  CRT288x_24CxProcess(int iMode ,WORD wStartAddr, int* uDataLength, BYTE lpData[]);




/** 
 * @fn		CRT288x_MifareKeyProcess() 
 * @detail	Mifare�����������
 * @see		...
 * @param	[in]iMode--����ģʽ   1 У�����룬 2 �������뵽EERPROM�� 3 �޸�����
 * @param	[in]iKs--��Կ����    0 KeyA�� 1 KeyB
 * @param	[in]iSn--������  (S50 card sn=00H-0FH, S70 card sn=00H-27H)
 * @param	[in][uDataLength--���������볤��
 * @param	[in]lpData--��������������(Ĭ�����룺FFFFFFFFFFFF)
 * @return	���,0�ɹ�����0ʧ�ܡ�
 * @exception ...
 *
 * @author	luowei
 * @date	2016/01/06
 */
int  CRT288x_MifareKeyProcess(int iMode, int iKs, int iSn, int uDataLength, BYTE lpData[]);




/** 
 * @fn		CRT288x_MifareCardProcess() 
 * @detail	Mifare������
 * @see		...
 * @param	[in]iMode--����ģʽ   1 �����������ݣ� 2 д���������ݣ� 3 S50 S70 ��ʼ����4 S50 S70 ���� 5 S50 S70 ��ֵ�� 6 S50 S70 ��ֵ
 * @param	[in]iSn--������  (Ultralight Card: iSn=00H-0FH, S50 card: iSn=00H-0FH, S70 card: iSn=00H-20H (iSn=21H-27H  S70 card �����8 ����������ÿһ��������16 ��))
 * @param	[in]iBn--������ʼ��� (Ultralight Card: iBn=00H, S50 card: iBn=00H-03H, S70 card: iBn=00H-03H  (iBn=00H-0FH   S70 card �����8 ����������ÿһ��������16 ��))
 * @param	[in]iLc--��������Ŀ (Ultralight Card: iLc=01H-10H, S50 card: iLc=01H-04H, S70 card: iLc=01H-04H  (iLc=01H-10H   S70 card �����8 ����������ÿһ��������16 ��))
 * @param	[in][out]uDataLength--���������ݳ���(S50 S70 ��ʼ������ֵ����ֵʱ Ϊ�����Ľ����)
 * @param	[in][out]lpData--����������(����д���� Ϊ���룬���ж����� Ϊ���)
 * @return	���,0�ɹ�����0ʧ�ܡ�
 * @exception ...
 *
 * @author	luowei
 * @date	2016/01/06
 */
int  CRT288x_MifareCardProcess(int iMode, int iSn, int iBn, int iLc, int* uDataLength, BYTE lpData[]);





/** 
 * @fn		CRT288C_GetHidCardNums() 
 * @detail	��ȡHid����
 * @see		...
 * @param	[out]szHidCardNums--��ȡ����Hid����
 * @return ���,0�ɹ�����0ʧ�ܡ�
 * @exception ...
 *
 * @author	luowei
 * @date	2016/01/06
 */
int CRT288C_GetHidCardNums(char szHidCardNums[]);



#endif 
