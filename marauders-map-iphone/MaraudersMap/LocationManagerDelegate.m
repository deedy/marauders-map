//
//  LocationManagerDelegate.m
//  MaraudersMap
//
//  Created by Debarghya Das on 5/5/14.
//  Copyright (c) 2014 Debarghya Das. All rights reserved.
//

#import "LocationManagerDelegate.h"

@interface LocationManagerDelegate()
- (void) stop;
@end

@implementation LocationManagerDelegate

- (void)locationManager:(CLLocationManager *)manager
     didUpdateLocations:(NSArray *)locations {
    // If it's a relatively recent event, turn off updates to save power.
    CLLocation* location = [locations lastObject];
    NSDate* eventDate = location.timestamp;
    NSTimeInterval howRecent = [eventDate timeIntervalSinceNow];
    if (abs(howRecent) < 15.0) {
        // If the event is recent, do something with it.
        NSLog(@"latitude %+.6f, longitude %+.6f\n",
              location.coordinate.latitude,
              location.coordinate.longitude);
    }
}

- (void)locationManager:(CLLocationManager *)manager
       didFailWithError:(NSError *)error
{
    printf("%s\n", "Sorry, I couldn't get your location.");
    [self stop];
}

- (void)stop
{
    CFRunLoopStop(CFRunLoopGetCurrent());
}

@end
