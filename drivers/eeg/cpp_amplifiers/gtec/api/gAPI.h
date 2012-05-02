/*------------------------------------------------------------------------------
 * Copyright (C) 2011 g.tec medical engineering GmbH.
 */

#ifndef GAPI_HPP_INCLUDED
#define GAPI_HPP_INCLUDED

/*------------------------------------------------------------------------------
 * Common defines for g.tec amplifier devices
 */
#define GT_NOS_AUTOSET -1
#define GT_BIPOLAR_DERIVATION_NONE -2
#define GT_FILTER_AUTOSET -1
#define GT_FILTER_NONE -2

/*------------------------------------------------------------------------------
 * Special defines for g.USBamp devices
 */
#define GT_USBAMP_NUM_DIGITAL_OUT 4
#define GT_USBAMP_NUM_REFERENCE 4
#define GT_USBAMP_NUM_GROUND 4
#define GT_USBAMP_NUM_ANALOG_IN 16
#define GT_USBAMP_RECOMMENDED_BUFFER_SIZE (32768 * 100)

/*------------------------------------------------------------------------------
 * Defines for interacting with g.tec APIs
 */
#define GT_TRUE 1
#define GT_FALSE 0

/*------------------------------------------------------------------------------
 * Typedefs for interacting with g.tec APIs
 */
typedef unsigned int gt_bool;
typedef unsigned long int gt_size;

/*------------------------------------------------------------------------------
 * Struct for non standard requests with g.tec APIs
 */
typedef struct special
{
  int what_;
  void* set_data_;
  gt_size set_data_num_elements_;
  void* get_data_;
  gt_size get_data_num_elements_;
} gt_special;

/*------------------------------------------------------------------------------
 * Struct to handle g.tec filters
 */
typedef struct filter_specification
{
  float f_upper;
  float f_lower;
  float sample_rate;
  float order;
  float type;
  gt_size id;
} gt_filter_specification;

/*------------------------------------------------------------------------------
 * Enums and typedefs for the g.USBamp device
 */
enum usbamp_special_commands { GT_GET_BANDPASS_COUNT, GT_GET_NOTCH_COUNT, GT_GET_BANDPASS_FILTER, GT_GET_NOTCH_FILTER, GT_GET_IMPEDANCE, GT_GET_CHANNEL_CALIBRATION, GT_SET_CHANNEL_CALIBRATION };
enum usbamp_device_mode { GT_MODE_NORMAL, GT_MODE_IMPEDANCE, GT_MODE_CALIBRATE, GT_MODE_COUNTER };
enum usbamp_analog_out_shape { GT_ANALOGOUT_SQUARE, GT_ANALOGOUT_SAWTOOTH, GT_ANALOGOUT_SINE, GT_ANALOGOUT_DRL, GT_ANALOGOUT_NOISE };

typedef enum usbamp_special_commands gt_usbamp_special_commands;
typedef enum usbamp_device_mode gt_usbamp_device_mode;
typedef enum usbamp_analog_out_shape gt_usbamp_analog_out_shape;

/*------------------------------------------------------------------------------
 * Struct to set or retrieve the calibration of the channels
 */
typedef struct usbamp_channel_calibration
{
  float scale[ GT_USBAMP_NUM_ANALOG_IN ];
  float offset[ GT_USBAMP_NUM_ANALOG_IN ];
} gt_usbamp_channel_calibration;

/*------------------------------------------------------------------------------
 * Struct to configure the internal signal generator of g.USBamp devices
 */
typedef struct usbamp_analog_out_config
{
  gt_usbamp_analog_out_shape shape;
  short int offset;
  short int frequency;
  short int amplitude;
} gt_usbamp_analog_out_config;

/*------------------------------------------------------------------------------
 * Overall struct to configure the g.USBamp device
 */
typedef struct usbamp_config
{
  unsigned short int sample_rate;
  int number_of_scans;
  gt_bool enable_trigger_line;
  gt_bool slave_mode;
  gt_bool enable_sc;
  gt_bool common_ground[ GT_USBAMP_NUM_GROUND ];
  gt_bool common_reference[ GT_USBAMP_NUM_REFERENCE ];
  gt_usbamp_device_mode mode;
  gt_bool scan_dio;
  float version;
  int bandpass[ GT_USBAMP_NUM_ANALOG_IN] ;
  int notch[ GT_USBAMP_NUM_ANALOG_IN ];
  int bipolar[ GT_USBAMP_NUM_ANALOG_IN ];
  unsigned char analog_in_channel[ GT_USBAMP_NUM_ANALOG_IN ];
  gt_size num_analog_in;
  gt_usbamp_analog_out_config* ao_config;
} gt_usbamp_config;

/*------------------------------------------------------------------------------
 * Overall struct to asynchron configure the g.USBamp device
 */
typedef struct usbamp_asynchron_config
{
  gt_bool digital_out[ GT_USBAMP_NUM_DIGITAL_OUT ];
} gt_usbamp_asynchron_config;

/*------------------------------------------------------------------------------
 * Common g.tec API functions
 */

#ifdef __cplusplus
extern "C" {
#endif

void GT_ShowDebugInformation( gt_bool show );
gt_bool   GT_UpdateDevices();
gt_size GT_GetDeviceListSize();
char** GT_GetDeviceList();
gt_bool   GT_FreeDeviceList( char** device_list, gt_size list_size );

gt_bool GT_OpenDevice( const char* device_name );
gt_bool GT_CloseDevice( const char* device_name );

gt_bool GT_SetConfiguration( const char* device_name, void* configuration );
gt_bool GT_GetConfiguration( const char* device_name, void* configuration );

gt_bool GT_SetAsynchronConfiguration( const char* device_name, void* configuration );
gt_bool GT_ApplyAsynchronConfiguration( const char* device_name );
gt_bool GT_GetAsynchronConfiguration( const char* device_name, void* configuration );

gt_bool GT_StartAcquisition( const char* device_name );
gt_bool GT_StopAcquisition( const char* device_name );

int  GT_GetSamplesAvailable( const char* device_name );
int  GT_GetData( const char* device_name, unsigned char* buffer, gt_size num_samples );
gt_bool GT_SetDataReadyCallBack( const char* device_name, void (*callback_function)(void*), void* data );
gt_bool GT_DoSpecial( const char* device_name, gt_special* data );

/*------------------------------------------------------------------------------
 * g.tec g.USBamp specific API functions
 */
gt_size GT_GetBandpassFilterListSize( const char* device_name, gt_size sample_rate );
gt_bool GT_GetBandpassFilterList( const char* device_name, gt_size sample_rate, gt_filter_specification* filter, gt_size filter_size );
gt_size GT_GetNotchFilterListSize( const char* device_name, gt_size sample_rate );
gt_bool GT_GetNotchFilterList( const char* device_name, gt_size sample_rate, gt_filter_specification* filter, gt_size filter_size );
gt_bool GT_GetChannelCalibration( const char* device_name, gt_usbamp_channel_calibration* calibration );
gt_bool GT_SetChannelCalibration( const char* device_name, gt_usbamp_channel_calibration* calibration );
gt_bool GT_Calibrate( const char* device_name, gt_usbamp_channel_calibration* calibration );
gt_bool GT_GetImpedance( const char* device_name, gt_size channel, int* impedance );

#ifdef __cplusplus
}
#endif

#endif // GAPI_HPP_INCLUDED
