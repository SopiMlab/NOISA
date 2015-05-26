// Based on sample code by Thalmic Labs Inc.
// Distributed under the Myo SDK license agreement. See LICENSE.txt for details.

// This code records latest the EMG data to a file. EMG streaming is only supported for one Myo at a time.

#ifdef _MSC_VER
#define _CRT_SECURE_NO_WARNINGS
#endif



#define _USE_MATH_DEFINES
#include <cmath>
#include <iomanip>
#include <algorithm>
#include <array>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <fstream>
#include <time.h>

#include <myo/myo.hpp>




class DataCollector : public myo::DeviceListener {
public:
	DataCollector()
	{
		openFiles();
	}


	void openFiles() {
		time_t timestamp = std::time(0);

		// Open file for EMG log
		if (emgFile.is_open()) {
			emgFile.close();
		}
		std::ostringstream emgFileString;
		emgFileString << "emg" << ".csv";
		emgFile.open(emgFileString.str(), std::ios::out);
	}

	// onEmgData() is called whenever a paired Myo has provided new EMG data, and EMG streaming is enabled.
	void onEmgData(myo::Myo* myo, uint64_t timestamp, const int8_t* emg)
	{
		double emg_avg = 0;
		emgFile.seekp(0);
		emgFile << timestamp;
		//std::cout << timestamp;
		for (size_t i = 0; i < 8; i++) {
			//emg_avg = emg_avg + static_cast<int>(emg[i]);
			//emg_avg = emg_avg + std::abs(emg[i]);
			emgFile << ',' << static_cast<int>(emg[i]);
			//std::cout << "test";

		}


		emgFile << std::endl;

	}

	void onConnect(myo::Myo *myo, uint64_t timestamp, myo::FirmwareVersion firmwareVersion) {
		//Reneable streaming
		myo->setStreamEmg(myo::Myo::streamEmgEnabled);
		openFiles();
	}


	// The files we are logging to
	std::ofstream emgFile;
};

int main(int argc, char** argv)
{
	// We catch any exceptions that might occur below -- see the catch statement for more details.
	try {


		// First, we create a Hub with our application identifier. Be sure not to use the com.example namespace when
		// publishing your application. The Hub provides access to one or more Myos.
		myo::Hub hub("com.example.emg-data-sample");

		std::cout << "Attempting to find a Myo..." << std::endl;

		// Next, we attempt to find a Myo to use. If a Myo is already paired in Myo Connect, this will return that Myo
		// immediately.
		// waitForMyo() takes a timeout value in milliseconds. In this case we will try to find a Myo for 10 seconds, and
		// if that fails, the function will return a null pointer.
		myo::Myo* myo = hub.waitForMyo(10000);

		// If waitForMyo() returned a null pointer, we failed to find a Myo, so exit with an error message.
		if (!myo) {
			throw std::runtime_error("Unable to find a Myo!");
		}

		// We've found a Myo.
		std::cout << "Connected to a Myo armband! Logging to the file system. Check the folder this appliation lives in." << std::endl << std::endl;

		// Next we enable EMG streaming on the found Myo.
		myo->setStreamEmg(myo::Myo::streamEmgEnabled);

		// Next we construct an instance of our DeviceListener, so that we can register it with the Hub.
		DataCollector collector;

		// Hub::addListener() takes the address of any object whose class inherits from DeviceListener, and will cause
		// Hub::run() to send events to all registered device listeners.
		hub.addListener(&collector);

		// Finally we enter our main loop.
		while (1) {
			// In each iteration of our main loop, we run the Myo event loop for a set number of milliseconds.
			// In this case, we wish to update our display 50 times a second, so we run for 1000/20 milliseconds.
			hub.run(1000/20);
		}

		// If a standard exception occurred, we print out its message and exit.
	}
	catch (const std::exception& e) {
		std::cerr << "Error: " << e.what() << std::endl;
		std::cerr << "Press enter to continue.";
		std::cin.ignore();
		return 1;
	}
}
