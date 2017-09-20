import {Component} from '@angular/core';

import {OffersService} from './offers.service';
import {Offer} from './offers.model';

@Component({
  selector: '<offers>',
  templateUrl: './offers.component.html',
  styleUrls: ['./offers.component.css'],
  providers: [OffersService]
})
export class OffersComponent {
  offers: Array<Offer>;

  constructor(private offersService: OffersService) {
  }

    ngOnInit() {
     this.offersService.getOffers()
      .subscribe(
        offers => {
            console.log(offers);
            this.offers = offers;
        }
      )
    }
}

