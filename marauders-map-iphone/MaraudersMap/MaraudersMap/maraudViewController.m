//
//  maraudViewController.m
//  MaraudersMap
//
//  Created by Debarghya Das on 5/5/14.
//  Copyright (c) 2014 Debarghya Das. All rights reserved.
//

#import "maraudViewController.h"

@interface maraudViewController ()

@end

@implementation maraudViewController
@synthesize myWebView;
@synthesize locationManager;

- (void)startStandardUpdates
{
    // Create the location manager if this object does not
    // already have one.
    if (nil == locationManager)
        locationManager = [[CLLocationManager alloc] init];
    locationManager.pausesLocationUpdatesAutomatically = YES;
    
    locationManager.delegate = self;
    locationManager.desiredAccuracy = kCLLocationAccuracyKilometer;
    
    // Set a movement threshold for new events.
    locationManager.distanceFilter = 1; // meters
    
    [locationManager startUpdatingLocation];
}


- (void)viewDidLoad
{
    [super viewDidLoad];
    
	// Do any additional setup after loading the view, typically from a nib.
//    self.myWebView.scalesPageToFit = YES;
    if (nil == locationManager)
        [self startStandardUpdates];
//    NSURL *url = [NSURL URLWithString:@"http://192.168.1.104:8888/index.html"];
    NSURL *url = [NSURL URLWithString:@"http://10.33.225.216:8888/"];
    NSURLRequest *request = [NSURLRequest requestWithURL:url];
    
    [self.myWebView loadRequest:request];
}

- (void)didReceiveMemoryWarning
{
    [super didReceiveMemoryWarning];
    // Dispose of any resources that can be recreated.
}

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
        
        NSString *current_player_id = [self.myWebView stringByEvaluatingJavaScriptFromString:@"globals.current_map_id"];
        NSString *current_map_id = [self.myWebView stringByEvaluatingJavaScriptFromString:@"globals.current_player_id"];
        NSString *baseurl = [self.myWebView stringByEvaluatingJavaScriptFromString:@"window.location.origin"];
        NSLog(@"map_id: %@, player_id:%@", current_map_id, current_player_id);
        
        NSString *player_url = [NSString stringWithFormat:@"%@%@", baseurl, @"/update_player"];
        
        NSLog(player_url);
        
        NSMutableURLRequest *request = [NSMutableURLRequest requestWithURL:[NSURL URLWithString:player_url]];
        
        NSString *lat = [[NSNumber numberWithDouble:location.coordinate.latitude] stringValue];
        NSString *lng = [[NSNumber numberWithDouble:location.coordinate.longitude] stringValue];
        
        NSString *params = [NSString stringWithFormat:@"player_id=%@&lat=%@&lng=%@", current_player_id, lat, lng];
        
        [request setHTTPMethod:@"POST"];
        [request setHTTPBody:[params dataUsingEncoding:NSUTF8StringEncoding]];
        [[NSURLConnection alloc] initWithRequest:request delegate:self];
        
    }
}

- (void)connection:(NSURLConnection *)connection didReceiveData:(NSData *)data {
    NSLog(data);
}

- (void)connection:(NSURLConnection *)connection didFailWithError:(NSError *)error {
    NSLog(@"Error with location update");
}

@end