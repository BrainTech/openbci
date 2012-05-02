/*
 * boost.h
 *
 *  Created on: 10-11-2011
 *      Author: Macias
 */

#ifndef BOOST_H_
#define BOOST_H_
/// 1st issue
#include <boost/asio/detail/pipe_select_interrupter.hpp>

/// 2nd issue
#ifdef __CYGWIN__
#include <termios.h>
#ifdef cfgetospeed
#define __cfgetospeed__impl(tp) cfgetospeed(tp)
#undef cfgetospeed
inline speed_t cfgetospeed(const struct termios *tp)
{
	return __cfgetospeed__impl(tp);
}
#undef __cfgetospeed__impl
#endif /// cfgetospeed is a macro

/// 3rd issue
#undef __CYGWIN__
#include <boost/asio/detail/buffer_sequence_adapter.hpp>
#define __CYGWIN__
#endif

#include <boost/asio.hpp>
#include <boost/asio/io_service.hpp>



#endif /* BOOST_H_ */
