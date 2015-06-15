//------------------------------------------------------------------------------
// <copyright file="MainWindow.xaml.cs" company="Microsoft">
//     Copyright (c) Microsoft Corporation.  All rights reserved.
// </copyright>
//------------------------------------------------------------------------------

namespace Microsoft.Samples.Kinect.FaceBasics
{
    using System;
    using System.Collections.Generic;
    using System.ComponentModel;
    using System.Diagnostics;
    using System.Globalization;
    using System.IO;
    using System.Linq;
    using System.Windows;
    using System.Windows.Media;
    using System.Windows.Media.Imaging;
    using System.Windows.Media.Media3D;
    using Microsoft.Kinect;
    using Microsoft.Kinect.Face;

    using OSC.NET;

    /// <summary>
    /// Interaction logic for MainWindow
    /// </summary>
    public partial class MainWindow : Window, INotifyPropertyChanged
    {
        /// <summary>
        /// Currently used KinectSensor
        /// </summary>
        private KinectSensor sensor = null;

        /// <summary>
        /// Body frame source to get a BodyFrameReader
        /// </summary>
        private BodyFrameSource bodySource = null;

        /// <summary>
        /// Body frame reader to get body frames
        /// </summary>
        private BodyFrameReader bodyReader = null;

        /// <summary>
        /// HighDefinitionFaceFrameSource to get a reader and a builder from.
        /// Also to set the currently tracked user id to get High Definition Face Frames of
        /// </summary>
        private HighDefinitionFaceFrameSource highDefinitionFaceFrameSource = null;

        /// <summary>
        /// HighDefinitionFaceFrameReader to read HighDefinitionFaceFrame to get FaceAlignment
        /// </summary>
        private HighDefinitionFaceFrameReader highDefinitionFaceFrameReader = null;


        /// <summary>
        /// Number of bodies tracked
        /// </summary>
        private int bodyCount;

        /// <summary>
        /// Array for the bodies
        /// </summary>
        private Body[] bodies = null;


        // X, Y, Z
        private Point3D instrument_1_pos = new Point3D(0.22, -0.17, 1.80); // set these according to the actual positions
        private Point3D instrument_2_pos = new Point3D(-0.26, -0.18, 1.77); // set these according to the actual positions
        private Point3D instrument_3_pos = new Point3D(-0.80, -0.18, 1.81); // set these according to the actual positions
        private Point3D audiencePos = new Point3D(4, 4, 4); // this can be one point in space along the way - not the actual audience



//        private Point3D instrument_1_pos = new Point3D(-0.49, -0.12, 1.67); // set these according to the actual positions
//        private Point3D instrument_2_pos = new Point3D(0.52, -0.1, 1.69); // set these according to the actual positions
//        private Point3D instrument_3_pos = new Point3D(0.05, -0.13, 1.62); // set these according to the actual positions
//        private Point3D audiencePos = new Point3D(4, 4, 4); // this can be one point in space along the way - not the actual audience

        private int leftHandProximity = 0;
        private int rightHandProximity = 0;

        /// <summary>
        /// FaceAlignment is the result of tracking a face, it has face animations location and orientation
        /// </summary>
        private FaceAlignment currentFaceAlignment = null;

        /// <summary>
        /// FaceModel is a result of capturing a face
        /// </summary>
        private FaceModel currentFaceModel = null;


        /// <summary>
        /// The currently tracked body
        /// </summary>
        private Body currentTrackedBody = null;

        /// <summary>
        /// The currently tracked body
        /// </summary>
        private ulong currentTrackingId = 0;

        /// <summary>
        /// Gets or sets the current tracked user id
        /// </summary>
        private string currentBuilderStatus = string.Empty;


        /// <summary>
        /// definition of bones
        /// </summary>
        private List<Tuple<JointType, JointType>> bones;

        /// <summary>
        /// Coordinate mapper to map one type of point to another
        /// </summary>
        private CoordinateMapper coordinateMapper = null;

        /// <summary>
        /// Width of display (depth space)
        /// </summary>
        private int displayWidth;

        /// <summary>
        /// Height of display (depth space)
        /// </summary>
        private int displayHeight;


        /// <summary>
        /// Face rotation display angle increment in degrees
        /// </summary>
        private const double RotationIncrementInDegrees = 1.0;

        //private string remoteIP = "127.0.0.1";
        private string remoteIP = "10.0.0.4";
        private int remotePort = 9000;

        private OSCTransmitter osc;


        /// <summary>
        /// Initializes a new instance of the MainWindow class.
        /// </summary>
        public MainWindow()
        {

            // one sensor is currently supported
            this.sensor = KinectSensor.GetDefault();
            this.bodyCount = this.sensor.BodyFrameSource.BodyCount;


            // get the coordinate mapper
            this.coordinateMapper = this.sensor.CoordinateMapper;

            // get the depth (display) extents
            FrameDescription frameDescription = this.sensor.DepthFrameSource.FrameDescription;

            // get size of joint space
            this.displayWidth = frameDescription.Width;
            this.displayHeight = frameDescription.Height;


            this.InitializeComponent();
            this.DataContext = this;



        }


        /// <summary>
        /// INotifyPropertyChangedPropertyChanged event to allow window controls to bind to changeable data
        /// </summary>
        public event PropertyChangedEventHandler PropertyChanged;



        /// <summary>
        /// Gets or sets the current tracked user id
        /// </summary>
        private ulong CurrentTrackingId
        {
            get
            {
                return this.currentTrackingId;
            }

            set
            {
                this.currentTrackingId = value;

            }
        }

        /// <summary>
        /// Returns the length of a vector from origin
        /// </summary>
        /// <param name="point">Point in space to find it's distance from origin</param>
        /// <returns>Distance from origin</returns>
        private static double VectorLength(CameraSpacePoint point)
        {
            var result = Math.Pow(point.X, 2) + Math.Pow(point.Y, 2) + Math.Pow(point.Z, 2);

            result = Math.Sqrt(result);

            return result;
        }

        /// <summary>
        /// Finds the closest body from the sensor if any
        /// </summary>
        /// <param name="bodyFrame">A body frame</param>
        /// <returns>Closest body, null of none</returns>
        private static Body FindClosestBody(BodyFrame bodyFrame)
        {
            Body result = null;
            double closestBodyDistance = double.MaxValue;

            Body[] bodies = new Body[bodyFrame.BodyCount];
            bodyFrame.GetAndRefreshBodyData(bodies);

            foreach (var body in bodies)
            {
                if (body.IsTracked)
                {
                    var currentLocation = body.Joints[JointType.SpineBase].Position;

                    var currentDistance = VectorLength(currentLocation);

                    if (result == null || currentDistance < closestBodyDistance)
                    {
                        result = body;
                        closestBodyDistance = currentDistance;
                    }
                }
            }

            return result;
        }

        /// <summary>
        /// Find if there is a body tracked with the given trackingId
        /// </summary>
        /// <param name="bodyFrame">A body frame</param>
        /// <param name="trackingId">The tracking Id</param>
        /// <returns>The body object, null of none</returns>
        private static Body FindBodyWithTrackingId(BodyFrame bodyFrame, ulong trackingId)
        {
            Body result = null;

            Body[] bodies = new Body[bodyFrame.BodyCount];
            bodyFrame.GetAndRefreshBodyData(bodies);

            foreach (var body in bodies)
            {
                if (body.IsTracked)
                {
                    if (body.TrackingId == trackingId)
                    {
                        result = body;
                        break;
                    }
                }
            }

            return result;
        }



        /// <summary>
        /// Fires when Window is Loaded
        /// </summary>
        /// <param name="sender">object sending the event</param>
        /// <param name="e">event arguments</param>
        private void Window_Loaded(object sender, RoutedEventArgs e)
        {
            osc = new OSCTransmitter(remoteIP, remotePort);
            this.InitializeHDFace();
        }

        /// <summary>
        /// Initialize Kinect object
        /// </summary>
        private void InitializeHDFace()
        {
            this.sensor = KinectSensor.GetDefault();
            this.bodySource = this.sensor.BodyFrameSource;
            this.bodyReader = this.bodySource.OpenReader();
            this.bodyReader.FrameArrived += this.BodyReader_FrameArrived;

            this.highDefinitionFaceFrameSource = new HighDefinitionFaceFrameSource(this.sensor);
            this.highDefinitionFaceFrameSource.TrackingIdLost += this.HdFaceSource_TrackingIdLost;

            this.highDefinitionFaceFrameReader = this.highDefinitionFaceFrameSource.OpenReader();
            this.highDefinitionFaceFrameReader.FrameArrived += this.HdFaceReader_FrameArrived;

            this.currentFaceModel = new FaceModel();
            this.currentFaceAlignment = new FaceAlignment();

            this.UpdateMesh();

            this.sensor.Open();
        }

        private static void ExtractRotationInDegrees(Vector4 rotQuaternion, out int pitch, out int yaw, out int roll)
        {
            double x = rotQuaternion.X;
            double y = rotQuaternion.Y;
            double z = rotQuaternion.Z;
            double w = rotQuaternion.W;

            // convert face rotation quaternion to Euler angles in degrees
            double yawD, pitchD, rollD;
            pitchD = Math.Atan2(2 * ((y * z) + (w * x)), (w * w) - (x * x) - (y * y) + (z * z)) / Math.PI * 180.0;
            yawD = Math.Asin(2 * ((w * y) - (x * z))) / Math.PI * 180.0;
            rollD = Math.Atan2(2 * ((x * y) + (w * z)), (w * w) + (x * x) - (y * y) - (z * z)) / Math.PI * 180.0;

            // clamp the values to a multiple of the specified increment to control the refresh rate
            double increment = RotationIncrementInDegrees;
            pitch = (int)(Math.Floor((pitchD + ((increment / 2.0) * (pitchD > 0 ? 1.0 : -1.0))) / increment) * increment);
            yaw = (int)(Math.Floor((yawD + ((increment / 2.0) * (yawD > 0 ? 1.0 : -1.0))) / increment) * increment);
            roll = (int)(Math.Floor((rollD + ((increment / 2.0) * (rollD > 0 ? 1.0 : -1.0))) / increment) * increment);

        }


        /// <summary>
        /// Sends the new deformed mesh to be drawn
        /// </summary>
        private void UpdateMesh()
        {
            //Debug.WriteLine("Jaw Open: " + this.currentFaceAlignment.AnimationUnits[FaceShapeAnimations.JawOpen]);
            var testi = this.currentFaceAlignment.FaceOrientation;
            int facePitch, faceYaw, faceRoll;
            ExtractRotationInDegrees(testi, out facePitch, out faceYaw, out faceRoll);

        }

        private void sendJointXYZ(JointType joint, string jointName)
        {
            var state = "Tracked";

            if (this.currentTrackedBody.Joints[JointType.HandRight].TrackingState.ToString().Equals(state) == true)
            {
                // osc.send(joint.x...)
            }
        }


        void sendFaceOrientationMessage(string focusPoint, double angle_1, double angle_2, double angle_3, double angle_aud)
        {
            OSCMessage msg = new OSCMessage("/faceOrientation");
            msg.Append(focusPoint);
            msg.Append((float)angle_1);
            msg.Append((float)angle_2);
            msg.Append((float)angle_3);
            msg.Append((float)angle_aud);
            osc.Send(msg);
        }

        void sendFaceTrackState(int state)
        {
            OSCMessage msg = new OSCMessage("/faceTrackState");
            msg.Append(state);
            osc.Send(msg);


        }

        void sendBodyTrackState(int state)
        {
            OSCMessage msg = new OSCMessage("/bodyTrackState");
            msg.Append(state);
            //osc.Send(msg);
            //Debug.WriteLine("Body: {0}", state);
        }

        private void BodyReader_FrameArrived(object sender, BodyFrameArrivedEventArgs e)
        {

            bool dataReceived = false;
           

            var frameReference = e.FrameReference;

            using (var frame = frameReference.AcquireFrame())
            {
                if (frame == null)
                {
                    sendBodyTrackState(0);
                    // We might miss the chance to acquire the frame, it will be null if it's missed
                    return;
                }


                if (frame != null)
                {
                    if (this.bodies == null)
                    {
                        this.bodies = new Body[frame.BodyCount];
                    }

                    // The first time GetAndRefreshBodyData is called, Kinect will allocate each Body in the array.
                    // As long as those body objects are not disposed and not set to null in the array,
                    // those body objects will be re-used.

                    
                    frame.GetAndRefreshBodyData(this.bodies);
                    dataReceived = true;
                }

                if (dataReceived)
                {

                    
                    Body selectedBody = FindClosestBody(frame);

                    if (selectedBody == null)
                    {
                        return;
                    }

                    this.currentTrackedBody = selectedBody;
                    this.CurrentTrackingId = selectedBody.TrackingId;

                    this.highDefinitionFaceFrameSource.TrackingId = this.CurrentTrackingId;


                    if (this.currentTrackedBody != null)
                    {
                        sendBodyTrackState(1);
                        
                        this.currentTrackedBody = FindBodyWithTrackingId(frame, this.CurrentTrackingId);
                        string state = "Tracked";
                        
                        // Orientations
                        // Lean and neck position

                        OSCMessage msgOrientation = new OSCMessage("/bodyOrientation");

                        var lean = this.currentTrackedBody.Lean;
                        msgOrientation.Append("lean");
                        msgOrientation.Append((float)lean.X);
                        msgOrientation.Append((float)lean.Y);

                        if (this.currentTrackedBody.Joints[JointType.Neck].TrackingState.ToString().Equals(state) == true)
                        {
                            var neckOrientation = this.currentTrackedBody.JointOrientations[JointType.Neck].Orientation; // Neck
                            int headPitch, headYaw, headRoll;
                            ExtractRotationInDegrees(neckOrientation, out headPitch, out headYaw, out headRoll);
                            msgOrientation.Append("neckOrientation");
                            msgOrientation.Append(headPitch);
                            msgOrientation.Append(headYaw);
                            msgOrientation.Append(headRoll);
                        }
                        osc.Send(msgOrientation);

                        // Joint positions
                        OSCMessage msgJointpos = new OSCMessage("/joint");
                        OSCMessage msgHandProximity = new OSCMessage("/handProximity");
                        var lhand = 0;
                        var rhand = 0;

                        if (this.currentTrackedBody.Joints[JointType.HandTipLeft].TrackingState.ToString().Equals(state) == true)
                        {
                            lhand = 1;
                            var joint = this.currentTrackedBody.Joints[JointType.HandTipLeft].Position;
                            msgJointpos.Append("handTipLeft");
                            msgJointpos.Append((float)joint.X);
                            msgJointpos.Append((float)joint.Y);
                            msgJointpos.Append((float)joint.Z);
                            //sendJointMessage("handTipLeft", handTipLeftPos);


                            float distance_1 = (float)Math.Sqrt(Math.Pow(joint.X - instrument_1_pos.X, 2) + Math.Pow(joint.Y - instrument_1_pos.Y, 2) + Math.Pow(joint.Z - instrument_1_pos.Z, 2));
                            float distance_2 = (float)Math.Sqrt(Math.Pow(joint.X - instrument_2_pos.X, 2) + Math.Pow(joint.Y - instrument_2_pos.Y, 2) + Math.Pow(joint.Z - instrument_2_pos.Z, 2));
                            float distance_3 = (float)Math.Sqrt(Math.Pow(joint.X - instrument_3_pos.X, 2) + Math.Pow(joint.Y - instrument_3_pos.Y, 2) + Math.Pow(joint.Z - instrument_3_pos.Z, 2));

                            float[] distances = new float[3] { distance_1, distance_2, distance_3 };
                            float min = distances.Min();

                            double threshold = 0.2;

                            if (min > 0.4)
                            {
                                string leftProximity = "far";
                                msgHandProximity.Append("handLeft");
                                msgHandProximity.Append(leftProximity);

                            }
                            if (min < threshold)
                            {
                                if (min == distance_1)
                                {
                                    string leftProximity = "instrument_1";
                                    msgHandProximity.Append("handLeft");
                                    msgHandProximity.Append(leftProximity);
                                }
                                if (min == distance_2)
                                {
                                    string leftProximity = "instrument_2";
                                    msgHandProximity.Append("handLeft");
                                    msgHandProximity.Append(leftProximity);
                                }
                                if (min == distance_3)
                                {
                                    string leftProximity = "instrument_3";
                                    msgHandProximity.Append("handLeft");
                                    msgHandProximity.Append(leftProximity);
                                }
                            }


                        }

                        if (this.currentTrackedBody.Joints[JointType.HandTipRight].TrackingState.ToString().Equals(state) == true)
                        {
                            rhand = 1;
                            var joint = this.currentTrackedBody.Joints[JointType.HandTipRight].Position;
                            msgJointpos.Append("handTipRight");
                            msgJointpos.Append((float)joint.X);
                            msgJointpos.Append((float)joint.Y);
                            msgJointpos.Append((float)joint.Z);

                            float distance_1 = (float)Math.Sqrt(Math.Pow(joint.X - instrument_1_pos.X, 2) + Math.Pow(joint.Y - instrument_1_pos.Y, 2) + Math.Pow(joint.Z - instrument_1_pos.Z, 2));
                            float distance_2 = (float)Math.Sqrt(Math.Pow(joint.X - instrument_2_pos.X, 2) + Math.Pow(joint.Y - instrument_2_pos.Y, 2) + Math.Pow(joint.Z - instrument_2_pos.Z, 2));
                            float distance_3 = (float)Math.Sqrt(Math.Pow(joint.X - instrument_3_pos.X, 2) + Math.Pow(joint.Y - instrument_3_pos.Y, 2) + Math.Pow(joint.Z - instrument_3_pos.Z, 2));

                            //double[] angles = new double[4] {angle_1, angle_2, angle_3, angle_aud};

                            float[] distances = new float[3] { distance_1, distance_2, distance_3 };
                            float min = distances.Min();
                            //Debug.WriteLine(" Right hand: X: {0}, Y: {1}, Z: {2} ", joint.X, joint.Y, joint.Z);
                            //Debug.WriteLine(" Right hand distance 1: {0}", distance_1);

                            double threshold = 0.2;

                            if (min > 0.4) 
                            {
                                string rightProximity = "far";
                                msgHandProximity.Append("handRight");
                                msgHandProximity.Append(rightProximity);
                            }

                            if (min < threshold)
                            {
                                if (min == distance_1)
                                {
                                    string rightProximity = "instrument_1";
                                    msgHandProximity.Append("handRight");
                                    msgHandProximity.Append(rightProximity);
                                }
                                if (min == distance_2)
                                {
                                    string rightProximity = "instrument_2";
                                    msgHandProximity.Append("handRight");
                                    msgHandProximity.Append(rightProximity);
                                }
                                if (min == distance_3)
                                {
                                    string rightProximity = "instrument_3";
                                    msgHandProximity.Append("handRight");
                                    msgHandProximity.Append(rightProximity);
                                }
                            }


                        }

                        if (this.currentTrackedBody.Joints[JointType.ThumbLeft].TrackingState.ToString().Equals(state) == true)
                        { 
                            var joint = this.currentTrackedBody.Joints[JointType.ThumbLeft].Position;
                            msgJointpos.Append("thumbLeft");
                            msgJointpos.Append((float)joint.X);
                            msgJointpos.Append((float)joint.Y);
                            msgJointpos.Append((float)joint.Z);

                        }

                        if (this.currentTrackedBody.Joints[JointType.ThumbRight].TrackingState.ToString().Equals(state) == true)
                        {
                            var joint = this.currentTrackedBody.Joints[JointType.ThumbRight].Position;
                            msgJointpos.Append("thumbRight");
                            msgJointpos.Append((float)joint.X);
                            msgJointpos.Append((float)joint.Y);
                            msgJointpos.Append((float)joint.Z);



                        }

                        if (this.currentTrackedBody.Joints[JointType.HandLeft].TrackingState.ToString().Equals(state) == true)
                        {
                            var joint = this.currentTrackedBody.Joints[JointType.HandLeft].Position;
                            msgJointpos.Append("handLeft");
                            msgJointpos.Append((float)joint.X);
                            msgJointpos.Append((float)joint.Y);
                            msgJointpos.Append((float)joint.Z);

                        }
                        if (this.currentTrackedBody.Joints[JointType.HandRight].TrackingState.ToString().Equals(state) == true)
                        {
                            var joint = this.currentTrackedBody.Joints[JointType.HandRight].Position;
                            msgJointpos.Append("handRight");
                            msgJointpos.Append((float)joint.X);
                            msgJointpos.Append((float)joint.Y);
                            msgJointpos.Append((float)joint.Z);


                        }

                        if (this.currentTrackedBody.Joints[JointType.WristLeft].TrackingState.ToString().Equals(state) == true)
                        {
                            var joint = this.currentTrackedBody.Joints[JointType.WristLeft].Position;
                            msgJointpos.Append("wristLeft");
                            msgJointpos.Append((float)joint.X);
                            msgJointpos.Append((float)joint.Y);
                            msgJointpos.Append((float)joint.Z);
                        }

                        if (this.currentTrackedBody.Joints[JointType.WristRight].TrackingState.ToString().Equals(state) == true)
                        {
                            var joint = this.currentTrackedBody.Joints[JointType.WristRight].Position;
                            msgJointpos.Append("wristRight");
                            msgJointpos.Append((float)joint.X);
                            msgJointpos.Append((float)joint.Y);
                            msgJointpos.Append((float)joint.Z);
                        }



                        if (this.currentTrackedBody.Joints[JointType.ElbowLeft].TrackingState.ToString().Equals(state) == true)
                        {
                            var joint = this.currentTrackedBody.Joints[JointType.ElbowLeft].Position;
                            msgJointpos.Append("elbowLeft");
                            msgJointpos.Append((float)joint.X);
                            msgJointpos.Append((float)joint.Y);
                            msgJointpos.Append((float)joint.Z);
                        }

                        if (this.currentTrackedBody.Joints[JointType.ElbowRight].TrackingState.ToString().Equals(state) == true)
                        {
                            var joint = this.currentTrackedBody.Joints[JointType.ElbowRight].Position;
                            msgJointpos.Append("elbowRight");
                            msgJointpos.Append((float)joint.X);
                            msgJointpos.Append((float)joint.Y);
                            msgJointpos.Append((float)joint.Z);
                        }

                        if (this.currentTrackedBody.Joints[JointType.ShoulderLeft].TrackingState.ToString().Equals(state) == true)
                        {
                            var joint = this.currentTrackedBody.Joints[JointType.ShoulderLeft].Position;
                            msgJointpos.Append("shoulderLeft");
                            msgJointpos.Append((float)joint.X);
                            msgJointpos.Append((float)joint.Y);
                            msgJointpos.Append((float)joint.Z);
                        }

                        if (this.currentTrackedBody.Joints[JointType.ShoulderRight].TrackingState.ToString().Equals(state) == true)
                        {
                            var joint = this.currentTrackedBody.Joints[JointType.ShoulderRight].Position;
                            msgJointpos.Append("shoulderRight");
                            msgJointpos.Append((float)joint.X);
                            msgJointpos.Append((float)joint.Y);
                            msgJointpos.Append((float)joint.Z);
                        }

                        if (this.currentTrackedBody.Joints[JointType.Head].TrackingState.ToString().Equals(state) == true)
                        {
                            var joint = this.currentTrackedBody.Joints[JointType.Head].Position;
                            msgJointpos.Append("head");
                            msgJointpos.Append((float)joint.X);
                            msgJointpos.Append((float)joint.Y);
                            msgJointpos.Append((float)joint.Z);
                        }

                        if (this.currentTrackedBody.Joints[JointType.SpineShoulder].TrackingState.ToString().Equals(state) == true)
                        {
                            var joint = this.currentTrackedBody.Joints[JointType.SpineShoulder].Position;
                            msgJointpos.Append("spineShoulder");
                            msgJointpos.Append((float)joint.X);
                            msgJointpos.Append((float)joint.Y);
                            msgJointpos.Append((float)joint.Z);
                        }

                        if (this.currentTrackedBody.Joints[JointType.Neck].TrackingState.ToString().Equals(state) == true)
                        {
                            var joint = this.currentTrackedBody.Joints[JointType.Neck].Position;
                            msgJointpos.Append("neck");
                            msgJointpos.Append((float)joint.X);
                            msgJointpos.Append((float)joint.Y);
                            msgJointpos.Append((float)joint.Z);
                        }

                        if (this.currentTrackedBody.Joints[JointType.SpineBase].TrackingState.ToString().Equals(state) == true)
                        {
                            var joint = this.currentTrackedBody.Joints[JointType.SpineBase].Position;
                            msgJointpos.Append("spineBase");
                            msgJointpos.Append((float)joint.X);
                            msgJointpos.Append((float)joint.Y);
                            msgJointpos.Append((float)joint.Z);
                        }


                        if (this.currentTrackedBody.Joints[JointType.SpineMid].TrackingState.ToString().Equals(state) == true)
                        {
                            var joint = this.currentTrackedBody.Joints[JointType.SpineMid].Position;
                            msgJointpos.Append("spineMid");
                            msgJointpos.Append((float)joint.X);
                            msgJointpos.Append((float)joint.Y);
                            msgJointpos.Append((float)joint.Z);
                        }

                        if (this.currentTrackedBody.Joints[JointType.HipLeft].TrackingState.ToString().Equals(state) == true)
                        {
                            var joint = this.currentTrackedBody.Joints[JointType.HipLeft].Position;
                            msgJointpos.Append("hipLeft");
                            msgJointpos.Append((float)joint.X);
                            msgJointpos.Append((float)joint.Y);
                            msgJointpos.Append((float)joint.Z);
                        }

                        if (this.currentTrackedBody.Joints[JointType.HipRight].TrackingState.ToString().Equals(state) == true)
                        {
                            var joint = this.currentTrackedBody.Joints[JointType.HipRight].Position;
                            msgJointpos.Append("hipRight");
                            msgJointpos.Append((float)joint.X);
                            msgJointpos.Append((float)joint.Y);
                            msgJointpos.Append((float)joint.Z);
                        }



                        osc.Send(msgJointpos);

                        if (rhand == 1 || lhand == 1) // Has to see both hands
                        {
                            //Debug.WriteLine(new Random().NextDouble());
                            osc.Send(msgHandProximity);
                        }


                        return;
                   
                    }


                }
             }
        }
        /// <summary>
        /// This event is fired when a tracking is lost for a body tracked by HDFace Tracker
        /// </summary>
        /// <param name="sender">object sending the event</param>
        /// <param name="e">event arguments</param>
        private void HdFaceSource_TrackingIdLost(object sender, TrackingIdLostEventArgs e)
        {
            var lostTrackingID = e.TrackingId;
            //Debug.WriteLine("Lost body");

            if (this.CurrentTrackingId == lostTrackingID)
            {
                this.CurrentTrackingId = 0;
                this.currentTrackedBody = null;     
                this.highDefinitionFaceFrameSource.TrackingId = 0;

                sendBodyTrackState(0);
                sendFaceTrackState(0);
            }
        }

        /// <summary>
        /// This event is fired when a new HDFace frame is ready for consumption
        /// </summary>
        /// <param name="sender">object sending the event</param>
        /// <param name="e">event arguments</param>
        private void HdFaceReader_FrameArrived(object sender, HighDefinitionFaceFrameArrivedEventArgs e)
        {
            using (var frame = e.FrameReference.AcquireFrame())
            {
                // We might miss the chance to acquire the frame; it will be null if it's missed.
                // Also ignore this frame if face tracking failed.
                if (frame == null || !frame.IsFaceTracked)
                {
                    sendFaceTrackState(0); 
                    return;

                }

                frame.GetAndRefreshFaceAlignmentResult(this.currentFaceAlignment);
                string state = "Tracked";
                sendFaceTrackState(1);

                if (this.currentTrackedBody.Joints[JointType.Head].TrackingState.ToString().Equals(state) == true)
                {
                    var head = this.currentTrackedBody.Joints[JointType.Head].Position;
                    var nose = this.currentFaceModel.CalculateVerticesForAlignment(this.currentFaceAlignment);
                    CameraSpacePoint noseTip = nose[(int)HighDetailFacePoints.NoseTip];
                    Point3D headPos = new Point3D(head.X, head.Y, head.Z);
                    Point3D nosePos = new Point3D(noseTip.X, noseTip.Y, noseTip.Z);

                    Vector3D noseVector3D = headPos - nosePos;
                    Vector3D noseIns_1 = nosePos - instrument_1_pos;
                    Vector3D noseIns_2 = nosePos - instrument_2_pos;
                    Vector3D noseIns_3 = nosePos - instrument_3_pos;
                    Vector3D noseAud = nosePos - audiencePos;

                    double angle_1 = Vector3D.AngleBetween(noseVector3D, noseIns_1);
                    double angle_2 = Vector3D.AngleBetween(noseVector3D, noseIns_2);
                    double angle_3 = Vector3D.AngleBetween(noseVector3D, noseIns_3);
                    double angle_aud = Vector3D.AngleBetween(noseVector3D, noseAud);

                    double[] angles = new double[4] {angle_1, angle_2, angle_3, angle_aud};
                    double min = angles.Min();

                    string pointOfInterest = "elsewhere";

                    if (min < 40)
                    {
                        if (min == angle_1)
                        {
                            pointOfInterest = "instrument_1";
                            //Debug.WriteLine("Instrument 1: {0}", angle_1);
                        }

                        if (min == angle_2)
                        {
                            pointOfInterest = "instrument_2";
                        }
                        if (min == angle_3)
                        {
                            pointOfInterest = "instrument_3";
                        }
                        if (min == angle_aud)
                        {
                            pointOfInterest = "audience";
                        }

                    }


                    sendFaceOrientationMessage(pointOfInterest, angle_1, angle_2, angle_3, angle_aud);

                    
                 }

                var quality = "High";
                if (this.currentFaceAlignment.Quality.ToString().Equals(quality) == true)
                {
                    //Debug.WriteLine("Quality: {1}, Jaw Open: {0}", this.currentFaceAlignment.AnimationUnits[FaceShapeAnimations.JawOpen], this.currentFaceAlignment.Quality);
                    OSCMessage msgFacevalue = new OSCMessage("/faceValue");

                    var jawOpen = this.currentFaceAlignment.AnimationUnits[FaceShapeAnimations.JawOpen];
                    var jawSlideRight = this.currentFaceAlignment.AnimationUnits[FaceShapeAnimations.JawSlideRight];
                    var leftEyeClosed = this.currentFaceAlignment.AnimationUnits[FaceShapeAnimations.LefteyeClosed];
                    var rightEyeClosed = this.currentFaceAlignment.AnimationUnits[FaceShapeAnimations.RighteyeClosed];
                    var leftCheekPuff = this.currentFaceAlignment.AnimationUnits[FaceShapeAnimations.LeftcheekPuff];
                    var rightCheekPuff = this.currentFaceAlignment.AnimationUnits[FaceShapeAnimations.RightcheekPuff];
                    var leftEyebrowLowerer = this.currentFaceAlignment.AnimationUnits[FaceShapeAnimations.LefteyebrowLowerer];
                    var rightEyebrowLowerer = this.currentFaceAlignment.AnimationUnits[FaceShapeAnimations.RighteyebrowLowerer];
                    var lipCornerDepressorLeft = this.currentFaceAlignment.AnimationUnits[FaceShapeAnimations.LipCornerDepressorLeft];
                    var lipCornerDepressorRight = this.currentFaceAlignment.AnimationUnits[FaceShapeAnimations.LipCornerDepressorRight];
                    var lipCornerPullerLeft = this.currentFaceAlignment.AnimationUnits[FaceShapeAnimations.LipCornerPullerLeft];
                    var lipCornerPullerRight = this.currentFaceAlignment.AnimationUnits[FaceShapeAnimations.LipCornerPullerRight];
                    var lipPucker = this.currentFaceAlignment.AnimationUnits[FaceShapeAnimations.LipPucker];
                    var lipStretcherLeft = this.currentFaceAlignment.AnimationUnits[FaceShapeAnimations.LipStretcherLeft];
                    var lipStretcherRight = this.currentFaceAlignment.AnimationUnits[FaceShapeAnimations.LipStretcherRight];
                    var lowerlipDepressorLeft = this.currentFaceAlignment.AnimationUnits[FaceShapeAnimations.LowerlipDepressorLeft];
                    var lowerlipDepressorRight = this.currentFaceAlignment.AnimationUnits[FaceShapeAnimations.LowerlipDepressorRight];

                    msgFacevalue.Append("jawOpen");
                    msgFacevalue.Append(jawOpen);
                    msgFacevalue.Append("jawSlideRight");
                    msgFacevalue.Append(jawSlideRight);
                    msgFacevalue.Append("leftEyeClosed"); 
                    msgFacevalue.Append(leftEyeClosed);
                    msgFacevalue.Append("rightEyeClosed"); 
                    msgFacevalue.Append(rightEyeClosed);
                    msgFacevalue.Append("leftCheekPuff");
                    msgFacevalue.Append(leftCheekPuff);
                    msgFacevalue.Append("rightCheekPuff"); 
                    msgFacevalue.Append(rightCheekPuff);
                    msgFacevalue.Append("leftEyebrowLowerer"); 
                    msgFacevalue.Append(leftEyebrowLowerer);
                    msgFacevalue.Append("rightEyebrowLowerer");
                    msgFacevalue.Append(rightEyebrowLowerer);
                    msgFacevalue.Append("lipCornerDepressorLeft"); 
                    msgFacevalue.Append(lipCornerDepressorLeft);
                    msgFacevalue.Append("lipCornerDepressorRight"); 
                    msgFacevalue.Append(lipCornerDepressorRight);
                    msgFacevalue.Append("lipCornerPullerLeft"); 
                    msgFacevalue.Append(lipCornerPullerLeft);
                    msgFacevalue.Append("lipCornerPullerRight"); 
                    msgFacevalue.Append(lipCornerPullerRight);
                    msgFacevalue.Append("lipPucker"); 
                    msgFacevalue.Append(lipPucker);
                    msgFacevalue.Append("lipStretcherLeft"); 
                    msgFacevalue.Append(lipStretcherLeft);
                    msgFacevalue.Append("lipStretcherRight"); 
                    msgFacevalue.Append(lipStretcherRight);
                    msgFacevalue.Append("lowerLipDepressorLeft"); 
                    msgFacevalue.Append(lowerlipDepressorLeft);
                    msgFacevalue.Append("lowerLipDepressorRight"); 
                    msgFacevalue.Append(lowerlipDepressorRight);

                    osc.Send(msgFacevalue);
                }
            }
        }




        /// <summary>
        /// Execute start up tasks
        /// </summary>
        /// <param name="sender">object sending the event</param>
        /// <param name="e">event arguments</param>
        private void MainWindow_Loaded(object sender, RoutedEventArgs e)
        {
            if (this.bodyReader != null)
            {
                this.bodyReader.FrameArrived += this.BodyReader_FrameArrived;
            }
        }

        /// <summary>
        /// Execute shutdown tasks
        /// </summary>
        /// <param name="sender">object sending the event</param>
        /// <param name="e">event arguments</param>
        private void MainWindow_Closing(object sender, CancelEventArgs e)
        {
            if (this.bodyReader != null)
            {
                // BodyFrameReader is IDisposable
                this.bodyReader.Dispose();
                this.bodyReader = null;
            }

            if (this.sensor != null)
            {
                this.sensor.Close();
                this.sensor = null;
            }
        }

    }
}
