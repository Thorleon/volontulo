import { Component } from '@angular/core';

import { UserService } from './user.service';

@Component({
  selector: 'home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css'],
  providers: [ UserService ]
})
export class HomeComponent {

  constructor (private userService: UserService) {

    this.userService.loginUser('deco.jezierski@gmail.com', 'firefox1')
      .subscribe(
        data => {console.log(data)},
        error => {console.log(error)}
      )
  }
}
