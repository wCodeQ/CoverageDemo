//
//  ViewController.m
//  coverageDemo
//
//  Created by wq on 2019/8/5.
//  Copyright © 2019 王前. All rights reserved.
//

#import "ViewController.h"
#import "cover_new_info.h"

@interface ViewController ()

@end

@implementation ViewController

- (void)viewDidLoad {
    [super viewDidLoad];
    // Do any additional setup after loading the view.
    
    NSString *diffFilePath = [[NSBundle mainBundle] pathForResource:@"diff" ofType:@".txt"];
    char *argv[2] = {"diff", (char *)[diffFilePath cStringUsingEncoding:NSUTF8StringEncoding]};
    main(2, argv);
}


@end
