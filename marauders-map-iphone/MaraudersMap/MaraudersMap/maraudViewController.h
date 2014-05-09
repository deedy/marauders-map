//
//  maraudViewController.h
//  MaraudersMap
//
//  Created by Debarghya Das on 5/5/14.
//  Copyright (c) 2014 Debarghya Das. All rights reserved.
//

#import <UIKit/UIKit.h>
#import <CoreLocation/CoreLocation.h>

@interface maraudViewController : UIViewController<CLLocationManagerDelegate, NSURLConnectionDataDelegate>
{
    __weak IBOutlet UIWebView *myWebView;
    IBOutlet CLLocationManager *locationManager;
    
}
@property (weak, nonatomic) IBOutlet UIWebView *myWebView;
@property (retain, nonatomic) IBOutlet CLLocationManager *locationManager;

@end
