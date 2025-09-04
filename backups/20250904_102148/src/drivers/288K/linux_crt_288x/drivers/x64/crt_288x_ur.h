#ifndef __CRT_288K_UR__
#define __CRT_288K_UR__
#include <stdbool.h>

#define BYTE unsigned char
#define WORD unsigned short 
#define DWORD unsigned int

//通讯协议
#define ENQ  0x05
#define ACK  0x06
#define NAK  0x15
#define EOT  0x04
#define CAN  0x18
#define STX  0xF2
#define ETX  0x03
#define US   0x1F

//错误码
#define CRT_ERRCOUNT                 -200
#define CRT_ERR_CMD                  (CRT_ERRCOUNT-1) //命令字错误
#define CRT_ERR_CMDPARAM             (CRT_ERRCOUNT-2) //命令参数错误
#define CRT_ERR_CMDDENIAL            (CRT_ERRCOUNT-3) //命令不能被执行
#define CRT_ERR_DEVNOTSUP            (CRT_ERRCOUNT-4) //硬件不支持
#define CRT_ERR_CMDDATA              (CRT_ERRCOUNT-5) //命令数据错误
#define CRT_ERR_LOCKCARD             (CRT_ERRCOUNT-11) //锁卡钩操作失败
#define CRT_ERR_EEPROM               (CRT_ERRCOUNT-15) //EEPROM error
#define CRT_ERR_TRACKCHECK           (CRT_ERRCOUNT-20) //读磁卡错（校验错）
#define CRT_ERR_READTRACK            (CRT_ERRCOUNT-21) //读磁卡错
#define CRT_ERR_POWERDOWN            (CRT_ERRCOUNT-30) //卡机掉电（Power down）
#define CRT_ERR_ICPROCESS            (CRT_ERRCOUNT-41) //IC卡模块操作失败
#define CRT_ERR_ICPOWERSHORT         (CRT_ERRCOUNT-60) //IC卡电源短路
#define CRT_ERR_ICACTIVATIONFAIL     (CRT_ERRCOUNT-61) //IC卡激活失败
#define CRT_ERR_ICDENIAL             (CRT_ERRCOUNT-62) //IC卡不支持当前命令
#define CRT_ERR_ICNOTRESPOND         (CRT_ERRCOUNT-63) //IC卡通讯出错
#define CRT_ERR_ICNOTRESPOND_OTHER   (CRT_ERRCOUNT-64) //IC卡通讯出错(其他)
#define CRT_ERR_ICNOTACTIVATION      (CRT_ERRCOUNT-65) //IC卡未激活
#define CRT_ERR_ICNOTSUP             (CRT_ERRCOUNT-66) //卡机不支持这种IC卡
#define CRT_ERR_ICEMV                (CRT_ERRCOUNT-66) //不支持EMV模式
#define CRT_ERR_COMMTIMEOUT	         (CRT_ERRCOUNT-80) //通讯失败超时
#define CRT_ERR_CANCEL	             (CRT_ERRCOUNT-84) //命令取消
#define CRT_ERR_PWDPROCESS	         (CRT_ERRCOUNT-90) //校验密码操作失败
#define CRT_ERR_PWDCHECK	         (CRT_ERRCOUNT-91) //密码校验失败
#define CRT_ERR_PWDSCRAP	         (CRT_ERRCOUNT-92) //密码校验失败，卡锁死
#define CRT_ERR_PWDADDROVERFLOW	     (CRT_ERRCOUNT-93) //操作地址溢出
#define CRT_ERR_PWDLENOVERFLOW	     (CRT_ERRCOUNT-94) //操作长度溢出
#define CRT_ERR_PWDPMERR	         (CRT_ERRCOUNT-95) //PM 错误
#define CRT_ERR_PWDCMERR	         (CRT_ERRCOUNT-96) //CM 错误
#define CRT_ERR_UNKNOWN              (CRT_ERRCOUNT-99) //未知错误

//打开设备
#define CRT_OPEN_TYPEUSB             0 //USB口方式打开设备
#define CRT_OPEN_TYPERS232           1 //RS232口方式打开设备

//初始化
#define CRT_INIT_NOTUNLOCK          0 //初始化无动作
#define CRT_INIT_UNLOCK             1 //初始化解锁


//卡状态
#define CRT_CARDST_NOCARD             1 //无卡
#define CRT_CARDST_INDOOR             2 //卡口
#define CRT_CARDST_INSIDE             3 //卡内
#define CRT_CARDST_UNKNOW             9 //设备不在线，卡状态未知

//锁卡状态
#define CRT_LOCKCARD_NOTLOCK            1 //未锁卡
#define CRT_LOCKCARD_LOCKED             2 //已锁卡
#define CRT_LOCKCARD_UNKNOW             9 //设备不在线,锁卡状态未知

//读卡器动作
#define CRT_RDACTION_NOACTION           0 //无动作
#define CRT_RDACTION_UNLOCK             1 //解锁
#define CRT_RDACTION_LOCKED             2 //锁卡
#define CRT_RDACTION_AUTOLOCKED         3 //有卡自动锁卡
#define CRT_RDACTION_NOTAUTOLOCK        4 //有卡不自动锁卡

//操作指示灯
#define  CRT_LED_RED                    0 //操作红色指示灯
#define  CRT_LED_BLUE                   1 //操作蓝色指示灯
#define  CRT_LED_ALL                    2 //操作所有指示灯

//灯控制
#define  CRT_LED_OFF                    0 //指示灯关闭
#define  CRT_LED_ON                     1 //指示灯打开
#define  CRT_LED_FLASHING               2 //指示灯闪烁

//磁条卡读取设置
#define CRT_SETMAGTYPE_READASCII        0x00000000 //以ASCII码读磁道数据
#define CRT_SETMAGTYPE_READHEX          0x00000001 //以二进制方式读磁道数据
#define CRT_SETMAGTYPE_AUTOUPLOAD       0x00000000 //主动上传磁道数据
#define CRT_SETMAGTYPE_NOTUPLOAD        0x00000010 //禁止主动上传磁道数据
#define CRT_SETMAGTYPE_EFFINSERT        0x00000000 //插入读磁道数据有效
#define CRT_SETMAGTYPE_EFFUPPLUG        0x00000100 //拔出读磁道数据有效

//读磁道数
#define CRT_ReadTracks_Track1           1 //磁道1数据
#define CRT_ReadTracks_Track2           2 //磁道2数据
#define CRT_ReadTracks_Track3           3 //磁道3数据

/** 
 * @fn		CRT288x_OpenConnection() 
 * @detail	打开设备
 * @see		...
 * @param	[in]iOpenMode--打开模式:0 USB连接模式， 1 RS232连接模式
 * @param	[in]iComPort--设置COM口(USB模式下，无需处理)
 * @param	[in]lBaudRate--设置波特率(默认 9600)
 * @return	结果,0成功，非0错误.
 * @exception ...
 * @example USB连接：int iRet = CRT288x_OpenConnection(0); 
            COM3,波特率9600 连接：int iRet = CRT288x_OpenConnection(1, 3, 9600);
 * @author	luowei
 * @date	2016/01/06
 */
int CRT288x_OpenConnection(int iOpenMode, int iComPort, long lBaudRate);



/** 
 * @fn		CRT288x_CloseConnection() 
 * @detail	关闭设备
 * @see		...
 * @return	结果,0成功，非0错误
 * @exception ...
 * @example int iRet = CRT288x_CloseConnection(); 
 * @author	luowei
 * @date	2016/01/06
 */
int CRT288x_CloseConnection();



/** 
 * @fn		CRT288x_ExeCommand() 
 * @detail	发送执行命令
 * @see		...
 * @param	[in]iSendDataLen:发送的命令长度
 * @param	[in]bySendData:发送的命令
 * @param	[out]iRecvDataLen:返回的命令长度
 * @param	[out]byRecvData:返回的命令
 * @param	[out]byStCode:返回的执行状态码
 * @return	结果,0成功，非0错误
 * @exception ...
 *
 * @author	luowei
 * @date	2016/01/06
 */
int  CRT288x_ExeCommand(int iSendDataLen, BYTE bySendData[] , int* iRecvDataLen, BYTE byRecvData[],BYTE byStCode[]);



/** 
 * @fn		CRT288x_InitDev() 
 * @detail	初始化设备
 * @see		...
 * @param	[in]InitMode--初始化模式:0 无动作， 1 解锁
 * @return	结果,0成功，非0错误
 * @exception ...
 *
 * @author	luowei
 * @date	2016/01/06
 */
int CRT288x_InitDev(int InitMode );


/** 
 * @fn		CRT288x_GetCardStatus() 
 * @detail	获取卡片状态
 * @see		...
 * @return	卡片状态: 1 无卡，2 卡在卡口， 3 卡在读卡器内， 9 设备不在线，卡状态未知。
 * @exception ...
 *
 * @author	luowei
 * @date	2016/01/06
 */
int  CRT288x_GetCardStatus();



/** 
 * @fn		CRT288x_GetLockStatus() 
 * @detail	获取锁卡状态
 * @see		...
 * @return	卡片状态: 1 未锁卡，2 已锁卡， 9 设备不在线，锁卡状态未知。
 * @exception ...
 *
 * @author	luowei
 * @date	2016/01/06
 */
int  CRT288x_GetLockStatus();



/** 
 * @fn		CRT288x_LockedProcess() 
 * @detail	锁卡操作
 * @see		...
 * @param	[in]iLockType--卡机锁卡操作:0 无动作， 1 解锁， 2 锁卡， 3 有卡自动锁卡， 4 有卡不自动锁卡
 * @return	结果,0成功，非0错误
 * @exception ...
 *
 * @author	luowei
 * @date	2016/01/06
 */
int  CRT288x_LockedProcess(int iLockType);



/** 
 * @fn		CRT288x_LEDProcess() 
 * @detail	指示灯操作
 * @see		...
 * @param	[in]iLightType--操作指示灯:0 红色指示灯，1 蓝色指示灯， 2 所有指示灯
 * @param	[in]iFlag--指示灯状态:0 灭，1 亮， 2 闪烁
 * @return	结果,0成功，非0错误
 * @exception ...
 *
 * @author	luowei
 * @date	2016/01/06
 */
int  CRT288x_LEDProcess(int iLightType, int iFlag);



/** 
 * @fn		CRT288x_SetLEDFlashTime() 
 * @detail	设置指示灯闪烁时间
 * @see		...
 * @param	[in]iOnTime--指示灯闪烁 亮时间: （0x00-0xFF）*0.25秒
 * @param	[in]iOffTime--指示灯闪烁 灭时间: （0x00-0xFF）*0.25秒
 * @return	结果,0成功，非0错误
 * @exception ...
 *
 * @author	luowei
 * @date	2016/01/06
 */
int  CRT288x_SetLEDFlashTime(int iOnTime, int iOffTime);



/** 
 * @fn		CRT288x_SetReaderMagType() 
 * @detail	设置读卡器读磁卡方式
 * @see		...
 * @param	[in]iReadMode--读卡方式: 0 ASCII码读卡数据， 1 二进制码读卡数据
 * @param	[in]iDataMode--数据有效方式: 0 插卡数据有效， 1 拔卡数据有效 
  * @param	[in]bAutoUpload--是否主动上传: TRUE 允许主动上传， FALSE 禁止主动上传 
 * @return	结果,0成功，非0错误
 * @exception ...
 *
 * @author	luowei
 * @date	2016/01/06
 */
int  CRT288x_SetReaderMagType(int iReadMode, int iDataMode, bool bAutoUpload);



/** 
 * @fn		CRT288x_ReadTrack() 
 * @detail	读单磁道数据
 * @see		...
 * @param	[in]iTrackNum--磁道号: 1 一磁道， 2 二磁道， 3 三磁道
 * @param	[out]szTrackData--返回磁道数据 
 * @return	结果,0成功，非0错误
 * @exception ...
 *
 * @author	luowei
 * @date	2016/01/06
 */
int  CRT288x_ReadTrack(int iTrackNum, char szTrackData[]);




/** 
 * @fn		CRT288x_ReadAllTracks() 
 * @detail	读所有磁道数据
 * @see		...
 * @param	[out]szTrack1Data--返回一磁道数据
 * @param	[out]szTrack2Data--返回二磁道数据
 * @param	[out]szTrack3Data--返回三磁道数据
 * @return	结果,0成功，非0错误
 * @exception ...
 *
 * @author	luowei
 * @date	2016/01/06
 */
int  CRT288x_ReadAllTracks(char szTrack1Data[], char szTrack2Data[], char szTrack3Data[]);



/** 
 * @fn		CRT288x_ClearTrackData() 
 * @detail	清除缓存区磁道数据
 * @see		...
 * @return	结果,0成功，非0错误
 * @exception ...
 *
 * @author	luowei
 * @date	2016/01/06
 */
int  CRT288x_ClearTrackData();



/** 
 * @fn		CRT288x_GetICType() 
 * @detail	获取(接触式)IC卡类型
 * @see		...
 * @return	结果,0 未知IC卡类型，非0失败， 10 T=0 CPU卡， 11 T=1 CPU卡， 20 SL4442卡， 21 SL4428卡， 30 AT24C01卡， 31 AT24C02卡， 32 AT24C04卡，
                 33 AT24C08卡， 34 AT24C16卡， 35 AT24C32卡， 36 AT24C64卡， 37 AT24C128卡， 38 AT24C256卡。 
 * @exception ...
 *
 * @author	luowei
 * @date	2016/01/06
 */
int  CRT288x_GetICType();



/** 
 * @fn		CRT288x_GetRFType() 
 * @detail	获取(非接触式)RF卡类型
 * @see		...
 * @return	结果,0 未知RF卡类型，非0失败， 110 S50卡， 111 S70卡， 112 UL卡， 120 TypeA CPU卡， 130 TypeB CPU卡。
 * @exception ...
 *
 * @author	luowei
 * @date	2016/01/06
 */
int  CRT288x_GetRFType();



/** 
 * @fn		CRT288x_ChipPower() 
 * @detail	IC卡上电操作
 * @see		...
 * @param	[in]iICType--IC卡类型:10 T=0 CPU卡， 11 T=1 CPU卡， 20 SL4442卡， 21 SL4428卡， 30 AT24C01卡， 31 AT24C02卡， 32 AT24C04卡，
							  33 AT24C08卡， 34 AT24C16卡， 35 AT24C32卡， 36 AT24C64卡， 37 AT24C128卡， 38 AT24C256卡
							  110 S50卡， 111 S70卡， 112 UL卡， 120 TypeA CPU卡， 130 TypeB CPU卡， 210 SAM 卡。
 * @param	[in]wChipPower--上电操作: 0x02 冷复位上电， 0x04 热复位上电， 0x08 下电。
 * @param	[out]byOutChipData--冷复位返回ATR数据
 * @param	[out]iOutChipDatalen--冷复位返回ATR数据长度
 * @return	结果,0成功，非0失败。
 * @exception ...
 *
 * @author	luowei
 * @date	2016/01/06
 */
int  CRT288x_ChipPower(int iICType, WORD wChipPower, BYTE byOutChipData[], int* iOutChipDatalen);




/** 
 * @fn		CRT288x_ChipIO() 
 * @detail	与IC卡芯片通讯
 * @see		...
 * @param	[in]wChipProtocol--IC卡通讯协议: 0 读卡器自动选择协议，1 T0协议， 2 T1协议。
 * @param	[in]ulInChipDataLength--发送APDU数据长度。
 * @param	[in]lpInbChipData--发送APDU数据
 * @param	[out]ulOutChipDataLength--返回的APDU数据长度
 * @param	[out]lpOutbChipData--返回的APDU数据
 * @return	结果,0成功，非0失败。
 * @exception ...
 *
 * @author	luowei
 * @date	2016/01/06
 */
int  CRT288x_ChipIO(WORD wChipProtocol, int ulInChipDataLength , BYTE lpInbChipData[], int* ulOutChipDataLength , BYTE lpOutbChipData[]);




/** 
 * @fn		CRT288x_GetCardActiveStatus() 
 * @detail	查询当前IC芯片的激活状态
 * @see		...
 * @return	结果,1 卡片已激活，当前CPU 卡工作时钟频率为3.57 MHZ， 2 卡片已激活，当前CPU 卡工作时钟频率为7.16 MHZ， 3 未激活， 9激活状态未知，非0失败。
 * @exception ...
 *
 * @author	luowei
 * @date	2016/01/06
 */
int  CRT288x_GetCardActiveStatus();




/** 
 * @fn		CRT288x_SAMSlotChange() 
 * @detail	SAM卡切换卡座
 * @see		...
 * @param	[in]iSamNum--需切换的卡座(1-10) 1 SAM1卡座， 2 SAM2卡座， 3 SAM3卡座， 4 SAM4卡座
 * @return	结果,0成功，非0失败。
 * @exception ...
 *
 * @author	luowei
 * @date	2016/01/06
 */
int  CRT288x_SAMSlotChange(int iSamNum);




/** 
 * @fn		CRT288x_SetVcc() 
 * @detail	设置上电Vcc属性
 * @see		...
 * @param	[in]iVcc--Vcc属性 1 5V电源，EMV方式激活， 2 5V电源，ISO7816方式激活， 3 3V电源，ISO7816方式激活
 * @return	结果,0成功，非0失败。
 * @exception ...
 *
 * @author	luowei
 * @date	2016/01/06
 */
int  CRT288x_SetVcc(int iVcc);




/** 
 * @fn		CRT288x_SL4442CheckPasswd() 
 * @detail	SL4442卡的校验密码
 * @see		...
 * @param	[in]iMode--操作模式 1 校验密码， 2 修改密码
 * @param	[in]uDataLength--密码的长度
 * @param	[in]lpData--校验的密码(默认密码：FFFFFF)
 * @return	结果,0成功，非0失败。
 * @exception 注意：用户要改写SLE4442卡数据必须知道卡的密码，密码错误计数器值会从2 或小于2 的值直至复位成零，当错误计数值为
 * 零时，卡片锁死报废。
 *
 * @author	luowei
 * @date	2016/01/06
 */
int  CRT288x_SL4442CheckPasswd(int iMode, int uDataLength, BYTE lpData[]);






/** 
 * @fn		CRT288x_SL4442Process() 
 * @detail	SL4442卡的读写操作
 * @see		...
 * @param	[in]iMode--操作模式   1 读， 2 写
 * @param	[in]iRegion--操作区域   1 主存储区， 2 保护位区， 3 安全区
 * @param	[in]wStartAddr--起始位置(0x00-0xFF)
 * @param	[in][out]uDataLength--操作的数据长度(主存储区：0-128， 保护位区：0-4， 安全区：0-4)
 * @param	[in][out]lpData--操作的数据(模式为写，此输入。 模式为读， 此输出)
 * @return	结果,0成功，非0失败。
 * @exception ...
 *
 * @author	luowei
 * @date	2016/01/06
 */
int  CRT288x_SL4442Process(int iMode, int iRegion ,WORD wStartAddr, int* uDataLength, BYTE lpData[]);






/** 
 * @fn		CRT288x_SL4428CheckPasswd() 
 * @detail	SL4428卡的校验密码
 * @see		...
 * @param	[in]iMode--操作模式 1 校验密码， 2 修改密码
 * @param	[in]uDataLength--密码的长度
 * @param	[in]lpData--校验的密码(默认密码：FFFF)
 * @return	结果,0成功，非0失败。
 * @exception 注意：用户要改写SLE4428卡数据必须知道卡的密码，密码错误计数器值会从7 或小于7 的值直至复位成零，当错误计数值为
 * 零时，卡片锁死报废。
 *
 * @author	luowei
 * @date	2016/01/06
 */
int  CRT288x_SL4428CheckPasswd(int iMode, int uDataLength, BYTE lpData[]);





/** 
 * @fn		CRT288x_SL4428Process() 
 * @detail	SL4428卡的读写操作
 * @see		...
 * @param	[in]iMode--操作模式   1 读， 2 写
 * @param	[in]iRegion--操作区域   1 主存储区， 2 保护位区
 * @param	[in]wStartAddr--起始位置(0x00-0x01FF)
 * @param	[in][out]uDataLength--操作的数据长度(主存储区：0-256， 保护位区：0-128)
 * @param	[in][out]lpData--操作的数据(模式为写，此输入。 模式为读， 此输出)
 * @return	结果,0成功，非0失败。
 * @exception ...
 *
 * @author	luowei
 * @date	2016/01/06
 */
int  CRT288x_SL4428Process(int iMode, int iRegion ,WORD wStartAddr, int* uDataLength, BYTE lpData[]);





/** 
 * @fn		CRT288x_24CxProcess() 
 * @detail	24Cx卡的读写操作
 * @see		...
 * @param	[in]iMode--操作模式   1 读， 2 写
 * @param	[in]wStartAddr--起始位置(24C01: 0x00-0x07F, 24C02: 0x00-0xFF, 24C04: 0x00-0x01FF, 24C08: 0x00-0x03FF, 24C16: 0x00-0x07FF,
                                 24C32: 0x00-0x0FFF, 24C64: 0x00-0x1FFF, 24C128: 0x00-0x3FFF, 24C256: 0x00-0x7FFF)
 * @param	[in][out]uDataLength--操作的数据长度
 * @param	[in][out]lpData--操作的数据(模式为写，此输入。 模式为读， 此输出)
 * @return	结果,0成功，非0失败。
 * @exception ...
 *
 * @author	luowei
 * @date	2016/01/06
 */
int  CRT288x_24CxProcess(int iMode ,WORD wStartAddr, int* uDataLength, BYTE lpData[]);




/** 
 * @fn		CRT288x_MifareKeyProcess() 
 * @detail	Mifare卡的密码操作
 * @see		...
 * @param	[in]iMode--操作模式   1 校验密码， 2 下载密码到EERPROM， 3 修改密码
 * @param	[in]iKs--密钥类型    0 KeyA， 1 KeyB
 * @param	[in]iSn--扇区号  (S50 card sn=00H-0FH, S70 card sn=00H-27H)
 * @param	[in][uDataLength--操作的密码长度
 * @param	[in]lpData--操作的密码数据(默认密码：FFFFFFFFFFFF)
 * @return	结果,0成功，非0失败。
 * @exception ...
 *
 * @author	luowei
 * @date	2016/01/06
 */
int  CRT288x_MifareKeyProcess(int iMode, int iKs, int iSn, int uDataLength, BYTE lpData[]);




/** 
 * @fn		CRT288x_MifareCardProcess() 
 * @detail	Mifare卡操作
 * @see		...
 * @param	[in]iMode--操作模式   1 读扇区块数据， 2 写扇区块数据， 3 S50 S70 初始化，4 S50 S70 读余额， 5 S50 S70 增值， 6 S50 S70 减值
 * @param	[in]iSn--扇区号  (Ultralight Card: iSn=00H-0FH, S50 card: iSn=00H-0FH, S70 card: iSn=00H-20H (iSn=21H-27H  S70 card 在最后8 个扇区中是每一个扇区是16 块))
 * @param	[in]iBn--操作起始块号 (Ultralight Card: iBn=00H, S50 card: iBn=00H-03H, S70 card: iBn=00H-03H  (iBn=00H-0FH   S70 card 在最后8 个扇区中是每一个扇区是16 块))
 * @param	[in]iLc--操作块数目 (Ultralight Card: iLc=01H-10H, S50 card: iLc=01H-04H, S70 card: iLc=01H-04H  (iLc=01H-10H   S70 card 在最后8 个扇区中是每一个扇区是16 块))
 * @param	[in][out]uDataLength--操作的数据长度(S50 S70 初始化，增值，减值时 为操作的金额数)
 * @param	[in][out]lpData--操作的数据(所有写操作 为输入，所有读操作 为输出)
 * @return	结果,0成功，非0失败。
 * @exception ...
 *
 * @author	luowei
 * @date	2016/01/06
 */
int  CRT288x_MifareCardProcess(int iMode, int iSn, int iBn, int iLc, int* uDataLength, BYTE lpData[]);





/** 
 * @fn		CRT288C_GetHidCardNums() 
 * @detail	获取Hid卡号
 * @see		...
 * @param	[out]szHidCardNums--获取到的Hid卡号
 * @return 结果,0成功，非0失败。
 * @exception ...
 *
 * @author	luowei
 * @date	2016/01/06
 */
int CRT288C_GetHidCardNums(char szHidCardNums[]);



#endif 
